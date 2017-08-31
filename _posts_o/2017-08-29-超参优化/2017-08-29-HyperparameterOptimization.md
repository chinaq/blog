---

layout:            post  
title:             "Hyperparameter Optimization"  
date:              2017-08-29 18:25:00 +0300  
tags:              ML
category:          Tech  
author:            Qiang  

---

## 针对 DLND p2 图片分类
- 手动设定 layers, thicks
- 随机选取 thicks
- 随机选取 layers, thicks
- 随机选取 layers，固定2倍 thicks

## 随机搜索
- Batch size (64, 128, 256, 512, 1024)
- conv layers (1, 2, 3)
- conv thick (32, 256)
- full layer (1, 2, 3)
- full thick (32, 256)
- keep prob (0.3-0.9)

## 结果
- 基本都保持在 68-72
- 缺点：似乎无论怎么调都不会提升识别率
- 优点：自动选参保证了识别率不会过低

## 还有哪些参数没有尝试
- learning rate (`*****` most important hyperpara)
- learning rate delay policy
- Batch Normalization type
- Pooling type
- Pooling window size
- conv striders size
- stimulate function type(relu, ...)

## 思考 - 接着该如何提高
### cs231n 最重要的是 learning rate
### cs231n 二次选取最优
### 读论文

## cs231n 笔记
### 想想




## 参考
- [使用Hyperopt自动选择超参数](https://mp.weixin.qq.com/s/-n-5Cp_hgkvdmsHGWEIpWw)
- [Neural networks for algorithmic trading. Hyperparameters optimization（同上英文版）](https://medium.com/@alexrachnog/neural-networks-for-algorithmic-trading-hyperparameters-optimization-cb2b4a29b8ee)
- [Hyperopt](https://github.com/hyperopt/hyperopt/wiki/FMin)
- [Introduction to Hyperopt for Optimizing Neural Networks](https://github.com/Vooban/Hyperopt-Keras-CNN-CIFAR-100/blob/master/IntroductionToHyperopt.ipynb)
- [Hyperopt for solving CIFAR-100 with a convolutional neural network (CNN) built with Keras and TensorFlow, GPU backend]( https://github.com/Vooban/Hyperopt-Keras-CNN-CIFAR-100)
- [Who is the best in CIFAR-10 ?](http://rodrigob.github.io/are_we_there_yet/build/classification_datasets_results.html#43494641522d3130)
- [cs231n - Hyperparameter optimization 小节（random search）](http://cs231n.github.io/neural-networks-3/)
