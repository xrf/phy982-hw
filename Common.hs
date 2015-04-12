{-# LANGUAGE BangPatterns #-}
module Common
  ( module Common
  , module Prelude
  , module Control.Monad
  , module Data.Complex
  , module Data.Foldable
  , module Data.Functor
  , module Data.List
  , module Data.Monoid
  , module Debug.Trace
  , module System.IO
  , Storable
  , Vector
  ) where
import Prelude hiding ((^))
import Control.Monad
import Data.Foldable (Foldable, foldl', for_)
import Data.Functor
import Data.Complex
import Data.List (intercalate)
import Data.Monoid
import Debug.Trace
import Foreign (Storable)
import Foreign.C
import Numeric.LinearAlgebra.Data (Vector)
import System.IO
import qualified Prelude as P
import qualified Numeric.LinearAlgebra.Data as L

(^) :: Num a => a -> Int -> a
(^) = (P.^)

zipV :: (Storable a, Storable b) => Vector a -> Vector b -> [(a, b)]
zipV xs ys = zip (L.toList xs) (L.toList ys)

zipV3 :: (Storable a, Storable b, Storable c) =>
         Vector a -> Vector b -> Vector c -> [(a, b, c)]
zipV3 xs ys zs = zip3 (L.toList xs) (L.toList ys) (L.toList zs)

showC :: (Show a, Num a, Ord a) => Complex a -> String
showC (x :+ y) = show x <> sign <> show y <> "i"
  where sign = if y >= 0 then "+" else ""

showD :: Double -> String
showD = show

showCD :: Complex Double -> String
showCD = showC

-- | Print a row of numbers separated by space.
hPrintRow :: Show a => Handle -> [a] -> IO ()
hPrintRow h = hPutStrLn h . unwords . (show <$>)

printRow :: Show a => [a] -> IO ()
printRow = hPrintRow stdout

check :: String -> Bool -> a -> a
check _ True  = id
check s False = error s

near0 :: (Num a, Ord a) => a -> a -> Bool
near0 dx x = abs x < dx

-- | Approximate derivative.
approxDiffC :: RealFloat a => a -> (a -> Complex a) -> a -> Complex a
approxDiffC dx f x = (f (x + dx / 2) - f (x - dx / 2)) / (dx :+ 0)

-- | Evaluate a Taylor series.
taylorSeries :: Num a =>
                a                       -- ^ origin of the series
             -> [a]                     -- ^ coefficients (must be finite)
             -> a                       -- ^ point of evaluation
             -> a
taylorSeries x0 cs x = eval 0 1 cs
  where dx = x - x0
        eval y _   []       = y
        eval y dxn (c : cs) = eval y' dxn' cs
          where !y'   = y + c * dxn
                !dxn' = dxn * dx

-- | Spherical Bessel function of the first kind.
sphericalBesselJ :: Int -> Double -> Double
sphericalBesselJ l x
  | l < 0     = error "sphericalBesselJ: l cannot be negative"
  | otherwise = realToFrac (c_gsl_sf_bessel_jl (fromIntegral l) (realToFrac x))
foreign import ccall unsafe "gsl/gsl_sf_bessel.h gsl_sf_bessel_jl"
  c_gsl_sf_bessel_jl :: CInt -> CDouble -> CDouble

-- | Spherical Bessel function of the second kind.
sphericalBesselY :: Int -> Double -> Double
sphericalBesselY l x
  | l < 0     = error "sphericalBesselY: l cannot be negative"
  | otherwise = realToFrac (c_gsl_sf_bessel_yl (fromIntegral l) (realToFrac x))
foreign import ccall unsafe "gsl/gsl_sf_bessel.h gsl_sf_bessel_yl"
  c_gsl_sf_bessel_yl :: CInt -> CDouble -> CDouble

diffSphericalBesselJ :: Int -> Double -> Double
diffSphericalBesselJ = diffSphericalBessel sphericalBesselJ

diffSphericalBesselY :: Int -> Double -> Double
diffSphericalBesselY = diffSphericalBessel sphericalBesselY

diffSphericalBessel :: (Int -> Double -> Double) -> Int -> Double -> Double
diffSphericalBessel f l x = fromIntegral l * f l x / x - f (1 + l) x
