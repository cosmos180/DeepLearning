'''
Author       : bughero jinxinhou@tuputech.com
Date         : 2024-03-27 17:28:17
LastEditors  : bughero jinxinhou@tuputech.com
LastEditTime : 2024-04-14 19:32:39
FilePath     : /DeepLearning/python/DeepLearningPython/pytorch/mnist.py
Description  : 

Copyright (c) 2024 by Antyme, All Rights Reserved. 
'''
import os
import torch
from torch import nn
from torch.utils.data import DataLoader
from torchvision import datasets, transforms
# import intel_extension_for_pytorch as ipex


from model_net.ConvNet import ConvNet

os.environ["KMP_DUPLICATE_LIB_OK"] = "TRUE"

# model_name = "mnist_1.1.pth"


# 定义超参数
batch_size = 64
learning_rate = 0.01
epochs = 100


# # 定义模型
# model = nn.Sequential(
#     nn.Flatten(),
#     nn.Linear(28*28, 512),
#     nn.ReLU(),
#     nn.Linear(512, 10)
# )

# device_xpu = torch.device("xpu")
# device_cpu = torch.device("cpu")
device_xpu = torch.device("cuda:0" if torch.cuda.is_available() else "cpu")

# model = ConvNet().to(device_xpu)
model = ConvNet().to(device_xpu)


def train(model_name: str):
    # 数据预处理
    transform = transforms.Compose([transforms.ToTensor()])

    # 加载MNIST数据集
    train_data = datasets.MNIST(
        root='./data', train=True, transform=transform, download=True)

    # 数据加载器
    train_loader = DataLoader(train_data, batch_size=batch_size, shuffle=True)

    # 定义损失函数和优化器
    criterion = nn.CrossEntropyLoss()
    optimizer = torch.optim.SGD(model.parameters(), lr=learning_rate)
    # optimizer = torch.optim.Adam(model.parameters(), lr=learning_rate)
    # optimizer = torch.optim.Adadelta(model.parameters(), lr=learning_rate)

    # 训练模型
    for epoch in range(epochs):
        for images, labels in train_loader:
            images, labels = images.to(device_xpu), labels.to(device_xpu)
            # 前向传播
            outputs = model(images)
            loss = criterion(outputs, labels)

            # 反向传播和优化
            optimizer.zero_grad()
            loss.backward()
            optimizer.step()

        if loss < 0.01:
            checkpoint = {
                "net": model.state_dict(),
                'optimizer': optimizer.state_dict(),
                "epoch": epoch
            }
            torch.save(
                checkpoint, 'ckpt_best_%s.pth' % (str(epoch)))
        print(f'Epoch {epoch+1}/{epochs}, Loss: {loss.item()}')

    print("模型训练完成！")
    torch.save(model.state_dict(), model_name)
    print("模型导出完成！")


def inference_with_checkpoint(path_checkpoint: str):
    checkpoint = torch.load(path_checkpoint)  # 加载断点
    model.load_state_dict(checkpoint['net'])  # 加载模型可学习参数

    optimizer = torch.optim.SGD(model.parameters(), lr=learning_rate)
    optimizer.load_state_dict(checkpoint['optimizer'])  # 加载优化器参数
    start_epoch = checkpoint['epoch']  # 设置开始的epoch
    # 将模型设置为评估模式
    model.eval()

    # 初始化计数器
    correct = 0
    total = 0

    # 数据预处理
    transform = transforms.Compose([transforms.ToTensor()])

    test_data = datasets.MNIST(root='./data', train=False,
                               transform=transform, download=True)

    test_loader = DataLoader(test_data, batch_size=batch_size, shuffle=False)

    # 不计算梯度
    with torch.no_grad():
        for images, labels in test_loader:
            # 前向传播
            outputs = model(images)
            # 获取预测结果
            _, predicted = torch.max(outputs.data, 1)
            # 更新计数器
            total += labels.size(0)
            correct += (predicted == labels).sum().item()

    # 计算准确率
    accuracy = 100 * correct / total
    print(f'在测试数据上的准确率: {accuracy}%, [{correct}/{total}]')


def inference(model_name: str):
    # 加载模型参数
    model.load_state_dict(torch.load(model_name))
    # 将模型设置为评估模式
    model.eval()

    # 初始化计数器
    correct = 0
    total = 0

    # 数据预处理
    transform = transforms.Compose([transforms.ToTensor()])

    test_data = datasets.MNIST(root='./data', train=False,
                               transform=transform, download=True)

    test_loader = DataLoader(test_data, batch_size=batch_size, shuffle=False)

    # 不计算梯度
    with torch.no_grad():
        for images, labels in test_loader:
            images, labels = images.to(device_xpu), labels.to(device_xpu)
            # 前向传播
            outputs = model(images)
            # 获取预测结果
            _, predicted = torch.max(outputs.data, 1)
            # 更新计数器
            total += labels.size(0)
            correct += (predicted == labels).sum().item()

    # 计算准确率
    accuracy = 100 * correct / total
    print(f'在测试数据上的准确率: {accuracy}%, [{correct}/{total}]')


def print_available_device():
    # 检查是否有可用的GPU
    if torch.cuda.is_available():
        print("Available GPUs:")
        # 获取GPU的数量
        num_gpus = torch.cuda.device_count()
        # 列出所有可用的GPU
        for i in range(num_gpus):
            print(f"Device {i}: {torch.cuda.get_device_name(i)}")
    else:
        print("No GPU is available.")

        print(torch.__version__)

        print(torch.__version__)
        # print(ipex.__version__)
        # [print(f'[{i}]: {torch.xpu.get_device_properties(i)}')
        #  for i in range(torch.xpu.device_count())]


def print_model_info(model_name: str):
    checkpoint = torch.load(model_name)  # 加载断点
    # print(checkpoint)

    model.load_state_dict(checkpoint['net'])  # 加载模型可学习参数
    print(model)

    print(count_parameters(model))

    # params = model.state_dict()

    # for key, value in params.items():
    #     print(key, value.size())
    #     print(value, type(value))
    #     break


def count_parameters(model):
    sum = 0
    for p in model.parameters():
        if p.requires_grad:
            print(f"p.numel() = {p.numel()}")
            sum += p.numel()

    return sum


print_available_device()
# train("mnist_GPU_1.4.pth")
# inference("mnist_1.1.pth")
inference("mnist_GPU_1.4.pth")
# inference_with_checkpoint("ckpt_best_13.pth")


# print_model_info("ckpt_best_13.pth")
# print_model_info("mnist_1.1.pth")
