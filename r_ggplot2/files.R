add2 <- function(a,b)
{
  a+b 
}

above10 <- function(x,y=10)
{
  use <- x>y
  x[use]
}

columnMean <- function(y, removeNa = TRUE)
{
  nc <- ncol(y)
  means <- numeric(nc)
  for (i in 1:nc)
  {
    means[i] <- mean(y[,i], na.rm = removeNa)
  }
  means
}