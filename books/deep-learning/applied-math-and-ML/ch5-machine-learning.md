# machine learning basic
machine learning is interesting because developing our understanding of machine learning entails developing our understanding of the principles that underlie intelligence.

## 5.1 machine learning tasks, T
+ classification
+ Classification with missing inputs: This kind of situation arises frequently in medical diagnosis, because many kinds of medical tests are expensive or invasive. One way to efficiently define such a large set of functions is to learn a probability distribution over all of the relevant variables, then solve the classification task by marginalizing out the missing variables.
+ Regression
+ Transcription: OCR, speech recognition
+ Machine translation
+ Structured output: One example is parsing—mapping a natural language sentence into a tree that describes its grammatical structure and tagging nodes of the trees as being verbs, nouns, or adverbs, and so on. Another example is pixel-wise segmentation of images, where the computer program assigns every pixel in an image to a specific category.
+ Anomaly detection
+ Synthesis and sampling: For example, in a speech synthesis task, we provide a written sentence and ask the program to emit an audio waveform containing a spoken version of that sentence.
+ Imputation of missing values
+ Denoising
+ Density estimation or probability mass function estimation

Of course, many other tasks and types of tasks are possible. The types of tasks we list here are intended only to provide examples of what machine learning can do, not to define a rigid taxonomy of tasks.

## 5.2 The Performance Measure, P
+ For tasks such as classification, classification with missing inputs, and transcription, we often measure the accuracy of the model.
+ We can also obtain equivalent information by measuring the error rate
+ For tasks such as density estimation, it does not make sense to measure accuracy, error rate, or any other kind of 0-1 loss.
+ In some cases, this is because it is difficult to decide what should be measured.
+ n other cases, we know what quantity we would ideally like to measure, but measuring it is impractical.

## 5.3 The Experience, E
Machine learning algorithms can be broadly categorized as unsupervised or supervised by what kind of experience they are allowed to have during the learning process.

Roughly speaking, unsupervised learning involves observing several examples of a random vector x, and attempting to implicitly or explicitly learn the probability distribution p(x), or some interesting properties of that distribution, while supervised learning involves observing several examples of a random vector x and an associated value or vector y, and learning to predict y from x, usually by estimating p(y|x).

Traditionally, people refer to regression, classification and structured output problems as supervised learning. Density estimation in support of other tasks is usually considered unsupervised learning.

One common way of describing a dataset is with a design matrix. A design matrix is a matrix containing a different example in each row.

In cases that any two example vectors have not the same size, rather than describing the dataset as a matrix with m rows, we will describe it as a set containing m elements: {x(1) , x(2) , . . . , x(m)}. 

## 5.4 Example: Linear Regression
We define input vector $x \in \R^n$ and output scalar $y \in R$. Let $\hat y$ be the value that our model predicts y should take on. 
$$ \large \hat y = w^T x$$
where w ∈ R n is a vector of parameters.

We thus have a definition of our task T: to predict y from x by outputting $ŷ = w^T x$. Next we need a definition of our performance measure P.
$$\Large MSE_{test} = \frac{1}{m} \sum \limits_{i} (\hat{y}^{(test)} - y^{(test)})_i^2$$
We can also see that
$$\Large MSE_{test} = \frac{1}{m} ||\hat{y}^{(test)} - y^{(test)}||_2^2$$

minimize the mean squared error on the training set, $MSE_train$.

## 5.5 capacity: overfitting and underfitting
The factors determining how well a machine learning algorithm will perform are its ability to:
1. Make the training error small.
2. Make the gap between training and test error small.

These two factors correspond to the two central challenges in machine learning: underfitting and overfitting. Underfitting occurs when the model is not able to obtain a sufficiently low error value on the training set. Overfitting occurs when the gap between the training error and test error is too large.

### weight decay -> regularization
We can increase one algorithms' capacity by adding functions from the hypothesis space of solutions the learning algorithms is able to choose. We can also give a learning algorithm a preference for one solution in its hypothesis space to another.

For example, we can modify the training criterion for linear regression to include weight decay.
$$ J(w) = MSE_{train} + \lambda w^T w$$

Regularization is any modification we make to a learning algorithm that is intended to reduce its generalization error but not its training error.

## 5.6 Hyperparameters and validation sets
Since the validation set is used to “train” the hyperparameters, the validation set error will underestimate the generalization error, though typically by a smaller amount than the training error. After all hyperparameter optimization is complete, the generalization error may be estimated using the test set.

The common used k-fold cross-validation procedure has one problem: there exist no unbiased estimators of the variance of the average error estimators used by this method.


## 5.7 estimators, bias and variance

### 5.7.1 point estimation
Let {x(1), . . . , x(m)} be a set of m independent and identically distributed (i.i.d.) data points. A point estimator or statistic is any function of the data:
$$ \hat θ_m = g(x^{(1)}, ...,x^{(m)})$$

### 5.7.2 Function Estimation
Here we are trying to predict a variable y given an input vector x. We assume that there is a function f(x) that describes the approximate relationship between y and x.

For example, $y = f(x) + \epsilon$, where $\epsilon$ stands for the part of y that is not predictable from x.

### 5.7.3 bias
The bias of an estimator is defined as:
$$ bias(\hat θ_m) = E(\hat θ_m) - θ$$
An estimator $\hat θ_m$ is said to be unbiased if bias($\hat θ_m) = 0$, which implies that $E(\hat θ_m) = θ$.

**The example in this section is very easy to read and really useful!**

### 5.7.4 variance
Variance is a property of the estimator that we might want to consider is how much we expect it to vary as a function of the data sample.
$$ variance = Var(\hat \theta)$$
$$ standard error = SE(\hat \theta) $$
The variance or the standard error of an estimator provides a measure of how we would expect the estimate we compute from data to vary as we independently resample the dataset from the underlying data generating process. Just as we might like an estimator to exhibit low bias we would also like it to have relatively low variance.

The standard error of the mean is very useful in machine learning experiments
$$ SE(\hat \mu_m) = \sqrt{Var[\frac{1}{m} \sum \limits_{i=1}^m x^{(i)}]} = \frac{σ}{\sqrt m}$$
This tells us why big data is needed.

### 5.7.5 trade off
Bias and variance measure two different sources of error in an estimator. Bias measures the expected deviation from the true value of the function or parameter. Variance on the other hand provides a measure of the deviation from the expected estimator value that any particular sampling of the data is likely to cause. 

Evaluating the MSE incorporates both the bias and the variance
$$ MSE = E[(\hat \theta_m - \theta)^2] = Bias(\hat \theta_m)^2 + Var(\hat \theta_m)$$
Increasing capacity tends to increase variance and decrease bias.

![](./graphs/capacity-bias-variance.png)

### 5.7.6 consistency
As the number of data points m in our dataset increases, our point estimates converge to the true value of the corresponding parameters. More formally, we would like that
$$ \large \mathop{lim}\limits_{m \to \infty} \hat \theta_m → \theta$$

## 5.8 maximum likelihood estimation