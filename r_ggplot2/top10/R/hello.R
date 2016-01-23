#' Building a model with top ten features
#'
#' This function develops a prediction algorithm based on the top 10 features
#' in 'x' that are most predictive of 'y'.
#'
#' @param x a n x p maxtri of n observation and p predictors
#' @param y a vector of lenght representing the response
#' @return a vector of coefficeint from final model with top 10 features.
#' @author Satyendra Raj Pandey
#' @details
#' This function runs a univariate regression of y on each predction in X and
#' calcuates a p-value indicating significance of the association. The final set of
#' 10 predictors is taken from the 10 smallest p-vales.
#' @seealso \code{lm}
#' @export
#' @importFrom stats lm

top10 <- function(x,y) {
  p <- ncol(x)
  if (p<10) stop("Thre are less than 10 predictors")
  pvalues <- numeric(p)
  for (i in seq_len(p)){
  fit <- lm(y~x[,i])
  summ <- summary(fit)
  pvalues <- summ$coefficients[2,4]
  }
  ord <- order(pvalues)
  ord <- ord[0:10]
  x10 <- x[, ord]
  fit <- lm(y~x10)
  coef(fit)
}

#' Prediction with top 10 featurres
#' This function takes a set of coefficients produced by the \code{top10}
#' @param X a n x 10 matrix containing a new observations
#' @param b
#' @return a numeric vector containing the predicted value
#' @export

predict10 <- function(X,b)
{
 X<- cbind(1,X)
 drop(X %*% b)
 }
