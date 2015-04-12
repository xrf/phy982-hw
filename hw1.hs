{-# LANGUAGE BangPatterns #-}
{- # LANGUAGE NoMonomorphismRestriction #-}
module Main where
import Prelude ()
import Common
import Numeric.LevMar (LevMarable, LevMarError, levmar)
import Numeric.LinearAlgebra.HMatrix (Element)
import Numeric.LinearAlgebra.Data
import Numeric.GSL.ODE
import Numeric.AD (auto, maclaurin)
import Numeric.AD.Rank1.Sparse (Sparse, jacobian')
import Numeric.AD.Mode.Tower (diff)
import qualified Numeric.LevMar as LM
import qualified Numeric.LinearAlgebra.Data as V

data LMOpts a =
  LMOpts
  { lmOptions :: !(LM.Options a)
  , lmMaxIter :: !Int
  , lmConstraints :: !(LM.Constraints a)
  }

defaultLMOpts :: Fractional a => LMOpts a
defaultLMOpts =
  LMOpts
  { lmOptions = LM.defaultOpts
  , lmMaxIter = 1000
  , lmConstraints = LM.Constraints Nothing Nothing Nothing Nothing
  }

-- | Return value: @(params, covariance_matrix, residual_sum_of_squares)@
levmarFit :: (LevMarable a, Storable a, Element a, Fractional a) =>
             LMOpts a                   -- ^ extra options
          -> ([Sparse a]
            -> Sparse a
            -> Sparse a)                -- ^ model function
          -> [a]                        -- ^ initial parameters
          -> ([a], [a])                 -- ^ data
          -> Either LevMarError ([a], [[a]], a)
levmarFit (LMOpts opts maxIter constraints) f p0 (x, y) =
  convertResults <$> levmar f' (Just j) p0' y' maxIter opts constraints
  where y'  = V.fromList y
        p0' = V.fromList p0
        f'  = V.fromList  . (fst <$>) . fj
        j   = V.fromLists . (snd <$>) . fj
        fj  = jacobian' (\ p -> f p . auto <$> x) . V.toList
        convertResults (p, i, s) = (V.toList p, V.toLists s, LM.infNorm2E i)

levmarFit_ :: (LevMarable a, Storable a, Element a, Fractional a) =>
              ([Sparse a]
             -> Sparse a
             -> Sparse a)                -- ^ model function
           -> [a]                        -- ^ initial parameters
           -> ([a], [a])                 -- ^ data
           -> Either LevMarError ([a], [[a]], a)
levmarFit_ = levmarFit defaultLMOpts

type Sign a = a -> a -> a

coulombF :: Int -> Double -> Double
coulombF l r =   r * sphericalBesselJ l r

coulombG :: Int -> Double -> Double
coulombG l r = - r * sphericalBesselY l r

diffCoulombF :: Int -> Double -> Double
diffCoulombF l r = sphericalBesselJ l r + r * diffSphericalBesselJ l r

diffCoulombG :: Int -> Double -> Double
diffCoulombG l r = -(sphericalBesselY l r + r * diffSphericalBesselY l r)

coulombH :: Sign Double -> Int -> Double -> Complex Double
coulombH (+-) l r = coulombG l r :+ 0 +- coulombF l r

diffCoulombH :: Sign Double -> Int -> Double -> Complex Double
diffCoulombH (+-) l r = diffCoulombG l r :+ 0 +- diffCoulombF l r

------------------------------------------------------------------------------

-- | Number of nucleons in Be-10 core
coreNucleons :: Num a => a
coreNucleons = 10

-- | Woods-Saxon radius [fm]
wsRadius :: Floating a => a
wsRadius = 1.2 * coreNucleons ** (1 / 3)

-- | Woods-Saxon radius [natural]
wsRadius' :: Floating a => a
wsRadius' = wsRadius / diffuseness

-- | Diffuseness [fm]
diffuseness :: Fractional a => a
diffuseness = 0.65

-- | Depth of the interaction [MeV]
depth :: Fractional a => a
depth = -61.1

-- | Twice the reduced mass [1/(MeV*fm^2)]
doubleMass :: Fractional a => a
doubleMass = 0.0478450

-- | Reduced mass [natural].
doubleMass' :: Fractional a => a
doubleMass' = doubleMass * diffuseness ^ 2 * abs depth

-- | Woods-Saxon potential [natural]
wsPotential :: Floating a => a -> a
wsPotential r = signum depth / (1 + exp (r - wsRadius'))

------------------------------------------------------------------------------

potential :: Floating a => a -> a
potential = wsPotential

pseudopotential :: Floating a => a -> a -> a
pseudopotential energy r = doubleMass' * (potential r - energy)

type ODE a = a -> [a] -> [a]

type ComplexODE a = a -> [Complex a] -> [Complex a]

odeSolveC :: ComplexODE Double
          -> [Complex Double]
          -> Vector Double
          -> Matrix (Complex Double)
odeSolveC f y = fromLists . (toComplex <$>) . toLists .
                odeSolve f' (fromComplex y)
  where f' t = fromComplex . f t . toComplex
        fromComplex (x :+ y : zs) = x : y : fromComplex zs
        fromComplex []            = []
        toComplex (x : y : zs) = x :+ y : toComplex zs
        toComplex []           = []
        toComplex [_]          = error "toComplex: length is not even"

equation :: (Ord a, Floating a) => a -> Int -> ODE a
equation energy l = f
  where f r [u, v] = [v, dvdr r u]
        f _ _      = error "expected 2 arguments"
        dvdr r u = (l' * (l' + 1) / r ^ 2 + pseudopotential energy r) * u
        l' = fromIntegral l

-- | A list of coefficients of the power series at the origin.
--   (Infinite list, starting at the zeroth power.)
uCoeffs :: Floating a => a -> Int -> [a]
uCoeffs energy l = take (l + 1) (repeat 0) <> (a0 : generate 1 a0 [])
  where generate n a as = a' : generate n' a' (a : as)
          where a' = sum (zipWith (*) bs as) / (n * (2 * fromIntegral l + n'))
                n' = n + 1
        bs = maclaurin (pseudopotential (auto energy)) 1
        a0 = 1

data SPWIn a =
  SPWIn
  { spwNumSteps :: Int
  , spwTaylorOrder :: Int
  , spwCrossoverRadius :: a
  , spwRadiusEnd :: a
  }

data SPWOut a =
  SPWOut
  { spwRadii :: Vector a
  , spwWavefunction :: Vector a
  , spwPartialS :: Complex a
  , spwAsymptoticWavefunction :: a -> a
  }

solvePartialWave :: SPWIn Double
                 -> Int
                 -> Double
                 -> SPWOut Double
solvePartialWave (SPWIn count n rc' re') l e' = SPWOut rs' us' s uaR
  where

    -- rescale energy
    e = e' / abs depth
    rc = rc' / diffuseness
    re = re' / diffuseness
    rs' = cmap (* diffuseness) rs

    -- momentum
    k = sqrt (doubleMass' * e)
    kC = k :+ 0

    -- approximate solution near origin
    n' = n + l + 1
    ux :: Floating a => a -> a
    ux = taylorSeries 0 (take n' (uCoeffs (realToFrac e) l))

    -- crossover point
    uc = ux rc
    vc = diff ux rc

    -- ODE
    rs = linspace count (rc, re)
    [us, vs] = toColumns (odeSolve (equation e l) [uc, vc] rs)

    -- inverse logarithmic derivative but without the radius
    rho  = us ! (count - 1) / vs ! (count - 1)
    rhoC = rho :+ 0

    -- S factor
    s = (coulombH (-) l (k * re) - kC * rhoC * diffCoulombH (-) l (k * re))
      / (coulombH (+) l (k * re) - kC * rhoC * diffCoulombH (+) l (k * re))

    -- asymptotic form of wavefunction
    ua r = coulombH (-) l (k * r) - s * coulombH (+) l (k * r)

    -- normalize the wavefunction
    uMax = maxElement (cmap abs us)
    us'  = cmap (/ uMax) us

    -- compute normalization factor
    fac = (us' ! (count - 1) :+ 0) / ua re
    uaR = realPart . (* fac) . ua . (/ diffuseness)

    -- sanity checks
    !_checks =
      check "|S| must be 1" (near0 1e-10 (magnitude s - 1)) $
      check "ua must be real [1]" (near0 1e-10 (imagPart (fac * ua 1))) $
      check "ua must be real [2]" (near0 1e-10 (imagPart (fac * ua 10))) $
      check "ua must be real [3]" (near0 1e-10 (imagPart (fac * ua re)))

phaseShift :: RealFloat a => Complex a -> Complex a
phaseShift s = (0 :+ (-0.5)) * log s

regularizeBy :: (RealFrac a, Floating a) => a -> [a] -> [a]
regularizeBy unit = go 0
  where go _ []       = []
        go y (x : xs) = x' : go x' xs
          where !x' = x + fromInteger (round ((y - x) / unit)) * unit

totalSumSquares :: (Foldable t, Num a) => a -> t a -> a
totalSumSquares c = foldl' (\ z x -> z + (x - c) ^ 2) 0

mean :: (Foldable t, Fractional a) => t a -> a
mean xs = z / n
  where (z, n) = foldl' (\ (z, n) x -> (z + x, n + 1)) (0, 0) xs

residualSumSquares :: Num a => [a] -> [a] -> a
residualSumSquares xs ys = foldl' (\ z (x, y) -> z + (x - y) ^ 2) 0 (zip xs ys)

coeffDet :: (Foldable t, Fractional a) => t a -> a -> a
coeffDet xs rss = 1 - rss / totalSumSquares (mean xs) xs

main :: IO ()
main = do
  putStrLn $ "R_ws = " <> showD wsRadius
  putStrLn ""

  withFile "hw1-u.dat" WriteMode $ \ file -> do
    hPutStrLn file "case l E R u"
    for_ ls $ \ l ->
      for_ es1 $ \ e -> do
        let SPWOut rs us s ua = solvePartialWave spwIn l e
        putStrLn . intercalate "; " $
          [ "E = " <> show e, "l = " <> show l ]
        putStrLn . unlines . (("  " <>) <$>) $
          [ "s     = " <> showC s
          , "delta = " <> show (realPart (phaseShift s)) ]
        for_ (zipV rs us) $ \ (r, u) -> do
          hPutStrLn file $ unwords
            [ "actual"
            , show l
            , show e
            , show r
            , show u
            ]
          hPutStrLn file $ unwords
            [ "asymptotic"
            , show l
            , show e
            , show r
            , show (ua r)
            ]

  withFile "hw1-delta.dat" WriteMode $ \ file -> do
    hPutStrLn file "case l E delta"
    for_ ls $ \ l -> do
      let deltas = regularizeBy pi $
                   realPart . phaseShift . spwPartialS .
                   solvePartialWave spwIn l <$> es2
      for_ (zip es2 deltas) $ \ (e, delta) -> do
        hPutStrLn file $ unwords
          [ "actual"
          , show l
          , show (e :: Double)
          , show delta
          ]

      when (l == 2) $ do
        putStrLn "fitting ..."
        let Right (p, sp, rss) = levmarFit_ f [1.3, 0.5, 0.1, 1.5] (es2, deltas)
            [ er,  gamma,  a,  b] = p
            [ser, sgamma, sa, sb] = sqrt <$> V.toList
                                    (takeDiag (V.fromLists sp))
            f'        = f [er, gamma, a, b]
            eFilter e = er - eWidth < e && e < er + eWidth
            eWidth    = gamma * 2
        writeFile "hw1-fit.dat" $ unlines
          [ "l E gamma a b"
          , unwords (show l : (show <$> p)) ]
        putStrLn . unlines . (("  " <>) <$>) $
          [ "E_r   = " <> show er    <> " +/- " <> show ser
          , "gamma = " <> show gamma <> " +/- " <> show sgamma
          , "a     = " <> show a     <> " +/- " <> show sa
          , "b     = " <> show b     <> " +/- " <> show sb
          , "Rsq   = " <> show (coeffDet deltas rss)
          ]
        for_ (filter eFilter es2) $ \ e ->
          hPutStrLn file $ unwords
            [ "fit"
            , show l
            , show (e :: Double)
            , show (f' e)
            ]

  where

    -- angular momentum
    ls = [0, 1, 2]

    -- energy
    es1 = [0.1, 3.0]
    es2 = [0.1, 0.12 .. 4.0]

    -- crossover radius
    rc = 0.001 * diffuseness

    -- radius where the potential becomes insignificant
    -- for a fractional precision of 'd':  re ~= wsRadius - log d
    re = (wsRadius - log du) * diffuseness where du = 1e-8

    -- number of steps in integration
    count = 1000

    -- order of Taylor approximation
    n = 5

    spwIn = SPWIn count n rc re

    -- model for resonance fitting
    f :: RealFloat a => [a] -> a -> a
    f [er, gamma, a, b] e = atan2 (0.5 * gamma) (er - e) + a * e + b
    f _                 _ = error "main.f: need exactly 4 params"
