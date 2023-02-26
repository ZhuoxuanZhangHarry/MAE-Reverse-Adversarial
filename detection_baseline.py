import os
import numpy as np
import torch
import torch.nn.functional as F
from detection_utils import Noisy, transform, random_label
import torch.optim as optim
import torchvision
from torchvision import transforms
from timm.data.constants import IMAGENET_DEFAULT_MEAN, IMAGENET_DEFAULT_STD

import torch.utils.data as data

''' 
- functions are called in evaluate.py in the other git repo
    - the detection functions are all helpers, only call the xx_vals
- single_metric_fpr_tpr in evaluate.py, evaluates all attacks over given criteria (l1/targeted/un)
- same for combined_metric_fpr_tpr, evaluates based on all three baselines
- tune_criterion_thresholds() function needs further reading
- .pt is pytorch file format


- TODO:
    - fix file format / TODO issues below
    - run evaluate on dataset to test
            $ python evaluate.py [-h] --real_dir REAL_DIR --adv_dir ADV_DIR --title TITLE
                     [--dataset DATASET] [--base BASE] [--lowbd LOWBD] 
                     [--upbd UPBD] [--fpr FPR] [--det_opt OPT]

        - real dir is validation set
        - adv_dir should be some new folder to store 
        - no 
'''

plain_transforms = transforms.Compose([
    transforms.ToTensor(),
    transforms.Resize(256), transforms.CenterCrop(224),
    transforms.Normalize(IMAGENET_DEFAULT_MEAN, IMAGENET_DEFAULT_STD)
])


# noisy = Noisy.forward # check that this works
# def l1_detection(model, 
#                 img, 
#                 dataset, 
#                 n_radius):
#     return torch.norm(F.softmax(model(transform(img, dataset=dataset))) - 
#                       F.softmax(model(transform(noisy(img, n_radius, dataset=dataset)))), 1).item()



def targeted_detection(model, img, true_label, dataset, lr, t_radius, cap=200, margin=20, use_margin=False):
    model.eval()
    # x_var = torch.autograd.Variable(img.clone().cuda(), requires_grad=True
    x_var = torch.autograd.Variable(img.clone(), requires_grad=True)
    # true_label = model(transform(x_var.clone(), dataset=dataset)).data.max(1, keepdim=True)[1][0].item()
    # change this function to pass in the true label

    optimizer_s = optim.SGD([x_var], lr=lr)
    # target_l = torch.LongTensor([random_label(true_label, dataset=dataset)]).cuda()
    target_l = torch.LongTensor([random_label(true_label, dataset=dataset)])
    counter = 0

    # while model(transform(x_var.clone(), dataset=dataset)).data.max(1, keepdim=True)[1][0].item() == true_label: 
    while model(x_var.clone()).data.max(1, keepdim=True)[1][0].item() == true_label:
        optimizer_s.zero_grad()
        # output = model(transform(x_var, dataset=dataset))
        output = model(x_var)
        if use_margin:
            target_l = target_l[0].item()
            _, top2_1 = output.data.cpu().topk(2)
            argmaxl1 = top2_1[0][0]
            if argmaxl1 == target_l:
                argmaxl1 = top2_1[0][1]
            loss = (output[0][argmaxl1] - output[0][target_l] + margin).clamp(min=0)
        else:
            loss = F.cross_entropy(output, target_l)
        loss.backward()

        x_var.data = torch.clamp(x_var - lr * x_var.grad.data, min=0, max=1)
        x_var.data = torch.clamp(x_var - img, min=-t_radius, max=t_radius) + img
        counter += 1
        if counter >= cap:
            break
    return counter

def untargeted_detection(model, 
                         img, 
                         dataset, 
                         lr, 
                         u_radius, 
                         cap=1000, 
                         margin=20, 
                         use_margin=False):
    model.eval()
    x_var = torch.autograd.Variable(img.clone().cuda(), requires_grad=True)
    true_label = model(transform(x_var.clone(), dataset=dataset)).data.max(1, keepdim=True)[1][0].item()
    optimizer_s = optim.SGD([x_var], lr=lr)
    counter = 0
    while model(transform(x_var.clone(), dataset=dataset)).data.max(1, keepdim=True)[1][0].item() == true_label:
        optimizer_s.zero_grad()
        output = model(transform(x_var, dataset=dataset))
        if use_margin:
            _, top2_1 = output.data.cpu().topk(2)
            argmaxl1 = top2_1[0][0]
            if argmaxl1 == true_label:
                argmaxl1 = top2_1[0][1]
            loss = (output[0][true_label] - output[0][argmaxl1] + margin).clamp(min=0)
        else: 
            loss = -F.cross_entropy(output, torch.LongTensor([true_label]).cuda())
        loss.backward()

        x_var.data = torch.clamp(x_var - lr * x_var.grad.data, min=0, max=1)
        x_var.data = torch.clamp(x_var - img, min=-u_radius, max=u_radius) + img
        counter += 1
        if counter >= cap:
            break
    return counter

def l1_vals(model, 
            dataset, 
            title, # type of attack
            attack, # can be 'real' or any attack name we choose
            lowind, # lowest index of the image to be sampled
            upind, # highest indx of the image to be sampled
            real_dir, #  root dir of real images
            adv_dir, # root dir of adversarial images
            n_radius): # noise radius
    vals = np.zeros(0)
    if attack == "real":
        # for i in range(lowind, upind):
        for folder, count in enumerate(real_dir, start=lowind):
            if count > upind:
                break
            # image_dir = os.path.join(real_dir, str(i) + '_img.pt')
            image_dir = os.path.join(real_dir, str(folder))
            assert os.path.exists(image_dir)
            view_data = torch.load(image_dir)
            model.eval()

            val = l1_detection(model, view_data, dataset, n_radius)
            vals = np.concatenate((vals, [val]))
    else:
        cout = upind - lowind
        for i in range(lowind, upind):
            # image_dir = os.path.join(os.path.join(adv_dir, attack), str(i) + title + '.pt')
            image_dir = os.path.join(os.path.join(adv_dir, attack), str(i) + title)

            assert os.path.exists(image_dir)
            adv = torch.load(image_dir)
            real_label = torch.load(os.path.join(real_dir, str(i) + '_label.pt'))
            model.eval()
            predicted_label = model(transform(adv.clone(), dataset=dataset)).data.max(1, keepdim=True)[1][0]
            if real_label == predicted_label:
                cout -= 1
                continue
            val = l1_detection(model, adv, dataset, n_radius)
            vals = np.concatenate((vals, [val]))
        print('this is the number of successes in l1 detection', cout)
    return vals

def targeted_vals(model, dataset, attack, real_dir, adv_dir, targeted_lr, t_radius):
    vals = np.zeros(0)
    if attack == "real":
        # for i in range(lowind, upind):

        # imagenet_path = "/Users/albertwen/Downloads/mae_data/ImageNet-Data/"
        image_dir = real_dir
        assert os.path.exists(image_dir)
        val_dataset = torchvision.datasets.ImageFolder(root=image_dir, transform=plain_transforms)
        val_dataset_loader = data.DataLoader(val_dataset, batch_size=1, shuffle=False, drop_last=False, num_workers=2)

        iters = 0
        for img, label in (val_dataset_loader):
            # image_dir = os.path.join(real_dir, str(i) + "_img.pt") # TODO: edit
            # assert os.path.exists(image_dir)
        
            model.eval()
            # print("targeted vals img", img)
            # print("targeted vals label", label)
            predicted_label = model(img.clone()).data.max(1, keepdim=True)[1][0]
            if label != predicted_label:
                continue

            val = targeted_detection(model, img, label, dataset, targeted_lr, t_radius)
            vals = np.concatenate((vals, [val]))
            iters += 1
            if iters > 5:
                break

    else: 
        cout = 0 # TODO: edit if statement logic

        iters = 0
        image_dir = adv_dir
        assert os.path.exists(image_dir)
        atk_dataset = torchvision.datasets.ImageFolder(root=image_dir, transform=plain_transforms)
        atk_dataset_loader = data.DataLoader(atk_dataset, batch_size=1, shuffle=False, drop_last=False, num_workers=2)

        for img, label in (atk_dataset_loader):
        # for i in range(lowind, upind):
            # image_dir = os.path.join(os.path.join(adv_dir, attack), str(i) + title + '.pt')
            # assert os.path.exists(image_dir)
            # adv = torch.load(image_dir)
            # real_label = torch.load(os.path.join(real_dir, str(i) + '_label.pt'))
            model.eval()
            predicted_label = model(img).data.max(1, keepdim=True)[1][0]
            real_label = label
            if real_label == predicted_label: # TODO: edit
                cout -= 1
                continue
            iters += 1
            if iters > 5:
                break
            val = targeted_detection(model, img, label, dataset, targeted_lr, t_radius)
            vals = np.concatenate((vals, [val]))
            
        print('this is the number of successes in targeted detection', cout)
    return vals

# def targeted_vals(model, 
#                   dataset, 
#                   attack, 
#                   lowind, 
#                   upind,
#                   real_dir, 
#                   adv_dir, 
#                   targeted_lr, 
#                   t_radius):
#     vals = np.zeros(0)
#     if attack == "real":
#         # for i in range(lowind, upind):

#         # imagenet_path = "/Users/albertwen/Downloads/mae_data/ImageNet-Data/"
#         image_dir = os.path.join(real_dir, 'val')
#         assert os.path.exists(image_dir)
#         val_dataset = torchvision.datasets.ImageFolder(root=image_dir, transform=plain_transforms)
#         val_dataset_loader = data.DataLoader(val_dataset, batch_size=1, shuffle=False, drop_last=False, num_workers=2)
#         for img, label in enumerate(val_dataset_loader):
#             # image_dir = os.path.join(real_dir, str(i) + "_img.pt") # TODO: edit
#             # assert os.path.exists(image_dir)
        
#             model.eval()

#             val = targeted_detection(model, img, dataset, targeted_lr, t_radius)
#             vals = np.concatenate((vals, [val]))
#     else: 
#         cout = upind - lowind # TODO: edit if statement logic

#         image_dir = os.path.join(adv_dir, attack)
#         assert os.path.exists(image_dir)
#         atk_dataset = torchvision.datasets.ImageFolder(root=image_dir, transform=plain_transforms)
#         atk_dataset_loader = data.DataLoader(atk_dataset, batch_size=1, shuffle=False, drop_last=False, num_workers=2)

#         for img, label in enumerate(atk_dataset_loader):

#         # for i in range(lowind, upind):
#             # image_dir = os.path.join(os.path.join(adv_dir, attack), str(i) + title + '.pt')
#             # assert os.path.exists(image_dir)
#             # adv = torch.load(image_dir)
#             # real_label = torch.load(os.path.join(real_dir, str(i) + '_label.pt'))
#             model.eval()
#             predicted_label = model(img).data.max(1, keepdim=True)[1][0]
#             real_label = label
#             if real_label == predicted_label: # TODO: edit
#                 cout -= 1
#                 continue
#             val = targeted_detection(model, img, dataset, targeted_lr, t_radius)
#             vals = np.concatenate((vals, [val]))
#         print('this is the number of successes in targeted detection', cout)
#     return vals

def untargeted_vals(model, 
                    dataset, 
                    title, 
                    attack, 
                    lowind, 
                    upind, 
                    real_dir, 
                    adv_dir, 
                    untargeted_lr, 
                    u_radius):
    vals = np.zeros(0)
    if attack == "real":
        for i in range(lowind, upind):
            image_dir = os.path.join(real_dir, str(i) + '_img.pt') # TODO: edit
            assert os.path.exists(image_dir)
            view_data = torch.load(image_dir)
            model.eval()
            val = untargeted_detection(model, view_data, dataset, untargeted_lr, u_radius)
            vals = np.concanate((vals, [val]))
    else: 
        cout = upind - lowind
        for i in range(lowind, upind):
            image_dir = os.path.join(os.path.join(adv_dir, attack), str(i) + title + '.pt') # TODO: edit
            assert os.path.exists(image_dir)
            adv = torch.load(image_dir)
            real_label = torch.load(os.path.join(real_dir, str(i) + "_label.pt")) # TODO: edit
            model.eval()
            predicted_label = model(transform(adv.clone(), dataset=dataset)).data.max(1, keepdim=True)[1][0]
            if real_label == predicted_label:
                count -= 1
                continue
            val = untargeted_detection(model, adv, dataset, untargeted_lr, u_radius)
            vals = np.concatenate((vals, [val]))
        print('this is the number of successes in untargeted detection', cout)
    return vals