# Week 14 — Introduction to Deep Learning with PyTorch

## Learning objectives

This week introduced artificial neural networks using PyTorch. The goal was to understand:

- What neurons, layers, weights, and biases are.
- How a neural network makes predictions.
- How a network learns through backpropagation and gradient descent.
- How loss functions measure prediction errors.
- How to train and evaluate binary and multiclass classifiers.
- Why accuracy alone is insufficient for imbalanced datasets.

---

## 1. What is a neural network?

A neural network is a mathematical model that learns relationships between input features and output labels.

It consists of interconnected computational units called neurons.

Each neuron:
1. Receives numerical inputs.
2. Multiplies each input by a weight.
3. Adds a bias.
4. Applies an activation function.
5. Passes the result to the next layer.

Weights and biases are trainable parameters. The network adjusts them during training to improve its predictions.

### Our neural network architecture

**Binary classification**

Input layer → Hidden layer → Output layer

- Input: 8,452 features
- Hidden layer: 128 neurons
- Activation: ReLU
- Output: 1 neuron
- Output activation: Sigmoid
- Trainable parameters: 1,082,113

**Multiclass classification**

Input layer → Hidden layer → Output layer

- Input: 7,954 features
- Hidden layer: 128 neurons
- Activation: ReLU
- Output: 5 neurons
- Output activation: None (raw logits)
- Trainable parameters: 1,018,885

### What do the layers do?

**Input layer**

Receives the numerical features. In our project, these are normalized 3-mer frequencies extracted from protein sequences.

**Hidden layer**

Learns combinations and patterns among input features. We used 128 neurons.

**Output layer**

Produces the final prediction.

For binary classification, one neuron produces a probability using sigmoid.

For multiclass classification, five neurons produce raw scores (logits), one for each resistance mechanism.

### Activation functions

**ReLU**

ReLU(x) = max(0, x)

It converts negative values to zero and retains positive values. It introduces nonlinearity, allowing the network to learn more complex relationships than a purely linear model.

**Sigmoid**

Sigmoid converts a numerical output into a value between 0 and 1.

We used it for binary classification, where the output represents the estimated probability of class 1.

**Softmax**

Softmax converts multiple logits into probabilities that sum to 1.

For our multiclass model, we did not add softmax explicitly because CrossEntropyLoss performs the necessary log-softmax calculation internally.

---

## 2. How does a neural network learn?

Training involves five main steps.

1. **Forward pass:** Input features pass through the network to generate predictions.
2. **Loss calculation:** A loss function measures the difference between predictions and true labels.
3. **Backpropagation:** The network calculates gradients, indicating how changes in individual parameters affect the loss.
4. **Weight updates:** An optimizer uses these gradients to adjust the parameters.
5. **Repetition:** The process continues over multiple epochs.

### Important terminology

- **Epoch:** One complete pass through the training dataset.
- **Loss:** A numerical measure of prediction error.
- **Gradient:** Indicates how the loss changes when a parameter changes.
- **Backpropagation:** Calculates gradients throughout the network.
- **Optimizer:** Updates model parameters using gradients.
- **Learning rate:** Controls the size of parameter updates.
- **Trainable parameters:** Weights and biases that the network learns.

### Our training configuration

| Parameter | Value |
|---|---|
| Framework | PyTorch |
| Optimizer | Adam |
| Learning rate | 0.001 |
| Epochs | 50 |
| Hidden neurons | 128 |
| Training approach | Full-batch |
| Hardware | CPU |

We used full-batch training: the entire training dataset was processed in each epoch.

---

## 3. Binary classification: AMR prediction

### Dataset

Source: `data/kmer_features.csv`

| Property | Value |
|---|---:|
| Total proteins | 2,158 |
| Numerical features | 8,452 |
| Class 0 | 1,079 |
| Class 1 | 1,079 |
| Training samples | 1,726 |
| Test samples | 432 |

We used an 80:20 stratified train-test split with random_state=42.

### Loss function

We used Binary Cross-Entropy Loss (BCELoss).

It measures the difference between predicted probabilities and binary labels.

The Adam optimizer adjusted the network weights to reduce this loss.

### Training loss

The initially trained model showed:

| Epoch | Training loss |
|---|---:|
| 10 | 0.6878 |
| 20 | 0.6788 |
| 30 | 0.6661 |
| 40 | 0.6493 |
| 50 | 0.6281 |

The decreasing loss indicates that the network was learning patterns in the training data.

Important reproducibility note: the evaluation command retrained the model with a fixed random seed. Therefore, this loss trajectory is from the initial training run, not necessarily the exact model used for the reported test metrics.

### Test results

| Metric | Class 0 | Class 1 |
|---|---:|---:|
| Precision | 0.8168 | 0.9882 |
| Recall | 0.9907 | 0.7778 |
| F1-score | 0.8954 | 0.8705 |

Overall accuracy: 88.43%

Macro F1-score: 0.8829

Confusion matrix:

| Actual / Predicted | Class 0 | Class 1 |
|---|---:|---:|
| Class 0 | 214 | 2 |
| Class 1 | 48 | 168 |

### Interpretation

The model correctly classified:

- 214 of 216 class 0 proteins.
- 168 of 216 class 1 proteins.

It missed 48 class 1 proteins.

If class 1 represents AMR-positive proteins, these 48 predictions are false negatives.

The model was very good at identifying class 0, but its recall for class 1 was lower.

**Lesson:** A model can achieve good overall accuracy while still missing a substantial proportion of positive cases.

---

## 4. Multiclass classification: resistance mechanisms

### Dataset

Source: `data/mechanism_kmer_features.csv`

| Property | Value |
|---|---:|
| Total proteins | 6,033 |
| Numerical features | 7,954 |
| Number of classes | 5 |
| Training samples | 4,826 |
| Test samples | 1,207 |

### Biological classes

| Label | Resistance mechanism | Total proteins |
|---|---|---:|
| 0 | Antibiotic inactivation | 5,239 |
| 1 | Antibiotic target alteration | 285 |
| 2 | Antibiotic efflux | 269 |
| 3 | Antibiotic target protection | 170 |
| 4 | Antibiotic target replacement | 70 |

### The class imbalance problem

Class 0 represents approximately 86.84% of the dataset.

The model could achieve high accuracy simply by predicting class 0 for every protein.

To address this, we used class-weighted CrossEntropyLoss.

Training class weights:

| Class | Weight |
|---|---:|
| 0 | 0.230 |
| 1 | 4.233 |
| 2 | 4.489 |
| 3 | 7.097 |
| 4 | 17.236 |

Rare classes received larger weights. Consequently, mistakes involving rare classes contributed more to the training loss.

**Important:** Class weighting does not create new examples or guarantee correct predictions. It changes how strongly the model is penalized for errors in different classes.

### Loss function

We used CrossEntropyLoss.

Unlike binary classification, the model has five output neurons.

Each neuron produces a raw score (logit). CrossEntropyLoss combines the probability calculation and loss calculation internally.

We used the Adam optimizer with a learning rate of 0.001 for 50 epochs.

### Training loss

| Epoch | Training loss |
|---|---:|
| 10 | 1.6004 |
| 20 | 1.5829 |
| 30 | 1.5577 |
| 40 | 1.5235 |
| 50 | 1.4794 |

The loss decreased, indicating that the network was learning from the training data.

However, training loss alone cannot establish how well the model predicts unseen proteins.

### Test results

| Mechanism | Precision | Recall | F1-score | Support |
|---|---:|---:|---:|---:|
| Inactivation | 1.0000 | 0.8616 | 0.9257 | 1,048 |
| Target alteration | 0.3438 | 0.9649 | 0.5069 | 57 |
| Efflux | 0.4324 | 0.8889 | 0.5818 | 54 |
| Target protection | 1.0000 | 0.6765 | 0.8070 | 34 |
| Target replacement | 1.0000 | 0.7143 | 0.8333 | 14 |

Overall accuracy: 86.08%

Macro F1-score: 0.7310

Weighted F1-score: 0.8861

### Confusion matrix

Rows represent actual classes; columns represent predicted classes.

| Actual / Predicted | 0 | 1 | 2 | 3 | 4 |
|---|---:|---:|---:|---:|---:|
| 0 | 903 | 87 | 58 | 0 | 0 |
| 1 | 0 | 55 | 2 | 0 | 0 |
| 2 | 0 | 6 | 48 | 0 | 0 |
| 3 | 0 | 9 | 2 | 23 | 0 |
| 4 | 0 | 3 | 1 | 0 | 10 |

### Understanding the results

**1. Why is accuracy misleading?**

If the model predicted class 0 for every test protein, its accuracy would be:

1,048 / 1,207 = 86.83%

Our neural network achieved 86.08% accuracy.

Thus, accuracy alone does not show an improvement over this simple majority-class baseline.

However, the majority-class model would completely fail to identify the other four mechanisms.

Our network did learn to identify minority classes, which is reflected in its macro F1-score of 0.731.

**2. Why is class 1 precision low?**

The model correctly identified 55 of 57 actual target-alteration proteins.

However, it also incorrectly classified many other proteins as class 1.

There were 160 predictions of class 1, but only 55 were correct.

Precision = 55 / 160 = 0.3438.

This means that only about 34% of its class 1 predictions were correct.

**3. Why is class 2 precision low?**

The model correctly identified 48 of 54 efflux proteins, but it also incorrectly assigned many other proteins to this class.

Precision = 48 / 111 = 0.4324.

**4. Why do classes 3 and 4 have 100% precision?**

The model made no false-positive predictions for these two classes in this particular test set.

However, their test sample sizes were small:

- Target protection: 34 proteins.
- Target replacement: 14 proteins.

Their precision estimates should therefore be interpreted cautiously.

**5. Did class weighting help?**

Class weighting encouraged the network to recognize rare mechanisms.

However, it also produced more false-positive predictions for target alteration and efflux.

We cannot establish how much class weighting helped without comparing it against an otherwise identical model trained without class weights.

---

## 5. Important evaluation metrics

### Accuracy

The proportion of all predictions that are correct.

Accuracy = Correct predictions / Total predictions

Useful, but potentially misleading with imbalanced datasets.

### Precision

Of all proteins predicted to belong to a particular class, how many actually belong to that class?

High precision means fewer false positives.

### Recall

Of all proteins that actually belong to a particular class, how many did the model identify?

High recall means fewer false negatives.

### F1-score

The harmonic mean of precision and recall.

F1 = 2 × (Precision × Recall) / (Precision + Recall)

It balances precision and recall.

### Macro F1

Calculate F1 separately for each class and then take the unweighted average.

Every class receives equal importance, regardless of its sample size.

### Weighted F1

Calculate F1 separately for each class, then average using the number of actual examples in each class as weights.

The majority class therefore has a much greater influence.

---

## 6. What did I learn?

1. Neural networks learn numerical relationships through adjustable weights and biases.
2. Hidden layers allow networks to learn nonlinear combinations of features.
3. Backpropagation calculates gradients used to update model parameters.
4. The optimizer uses gradients to reduce the loss.
5. Training loss and test performance measure different things.
6. Binary and multiclass classification require different output configurations and loss functions.
7. Class imbalance can make accuracy misleading.
8. Class weighting changes the importance of errors but does not guarantee better predictions.
9. A complex neural network does not automatically outperform simpler ML models.
10. Biological interpretation requires understanding both the predictions and the limitations of the dataset.

---

## 7. Limitations and next steps

These experiments are educational demonstrations, not validated biological prediction models.

Important limitations:

- Only one stratified random train-test split was used.
- No independent external test dataset was used.
- No validation set or systematic hyperparameter tuning was performed.
- We did not test sequence-identity-aware splitting. Closely related proteins could occur in both training and test sets, potentially inflating performance.
- The neural networks have approximately one million trainable parameters, which creates a risk of overfitting.
- The multiclass class-weighted model was not compared with an otherwise identical unweighted model.
- Performance on the rarest class is uncertain because only 14 examples were present in the test set.

### Future experiments

1. Compare weighted and unweighted CrossEntropyLoss.
2. Compare neural networks with logistic regression and random forest using identical splits and metrics.
3. Evaluate using cross-validation.
4. Investigate sequence-identity-aware splitting to assess generalization to less-related proteins.
5. Explore regularization, dropout, and early stopping.
6. Examine whether different feature representations improve mechanism classification.

### Final takeaway

The purpose of this week was to understand how a neural network works, not to prove that deep learning is the best approach for AMR prediction.

The central lesson is:

**A model is useful not because it is complex, but because it makes reliable predictions on genuinely unseen data.**
