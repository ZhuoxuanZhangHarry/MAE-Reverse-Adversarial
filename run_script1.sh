#!/usr/bin/env bash


# CUDA_VISIBLE_DEVICES=1  python3  run_reconstruct_mae.py --data_path /local/rcs/yunyun/ImageNet-Data/Attack/val/fgsm_8/ --mask_ratio 0.75 --model pretrain_mae_base_patch16_224 --batch_size 16 --resume output/reconstruct_mae_v2_pretrain_model/checkpoint-109.pth --mlp_resume output/reconstruct_mae_v2_pretrain_model/mlp-checkpoint-109.pth --output_dir output/reconstruct_mae_v2_pretrain_model/attack_iters_log/  --eval
# CUDA_VISIBLE_DEVICES=1  python3  run_reconstruct_mae.py --data_path /local/rcs/yunyun/ImageNet-Data/Attack/val/pgd_8/ --mask_ratio 0.75 --model pretrain_mae_base_patch16_224 --batch_size 16 --resume output/reconstruct_mae_v2_pretrain_model/checkpoint-109.pth --mlp_resume output/reconstruct_mae_v2_pretrain_model/mlp-checkpoint-109.pth --output_dir output/reconstruct_mae_v2_pretrain_model/attack_iters_log/  --eval
# CUDA_VISIBLE_DEVICES=1  python3  run_reconstruct_mae.py --data_path /local/rcs/yunyun/ImageNet-Data/Attack/val/pgd_16/ --mask_ratio 0.75 --model pretrain_mae_base_patch16_224 --batch_size 16 --resume output/reconstruct_mae_v2_pretrain_model/checkpoint-109.pth --mlp_resume output/reconstruct_mae_v2_pretrain_model/mlp-checkpoint-109.pth --output_dir output/reconstruct_mae_v2_pretrain_model/attack_iters_log/  --eval


CUDA_VISIBLE_DEVICES=2  python3  run_reconstruct_mae.py --data_path /local/rcs/yunyun/ImageNet-Data/Attack/val/fgsm_4/  --mask_ratio 0.75 --model pretrain_mae_base_patch16_224 --batch_size 16 --resume output/reconstruct_mae_v2_pretrain_model/checkpoint-109.pth --mlp_resume output/reconstruct_mae_v2_pretrain_model/mlp-checkpoint-109.pth --output_dir output/reconstruct_mae_v2_pretrain_model/attack_iters_log/ --output_fn fgsm4_epsilon.log.txt --eval

CUDA_VISIBLE_DEVICES=2  python3  run_reconstruct_mae.py --data_path /local/rcs/yunyun/ImageNet-Data/Attack/val/fgsm_8/  --mask_ratio 0.75 --model pretrain_mae_base_patch16_224 --batch_size 16 --resume output/reconstruct_mae_v2_pretrain_model/checkpoint-109.pth --mlp_resume output/reconstruct_mae_v2_pretrain_model/mlp-checkpoint-109.pth --output_dir output/reconstruct_mae_v2_pretrain_model/attack_iters_log/ --output_fn fgsm8_epsilon.log.txt --eval

CUDA_VISIBLE_DEVICES=2  python3  run_reconstruct_mae.py --data_path /local/rcs/yunyun/ImageNet-Data/Attack/val/pgd_8/  --mask_ratio 0.75 --model pretrain_mae_base_patch16_224 --batch_size 16 --resume output/reconstruct_mae_v2_pretrain_model/checkpoint-109.pth --mlp_resume output/reconstruct_mae_v2_pretrain_model/mlp-checkpoint-109.pth --output_dir output/reconstruct_mae_v2_pretrain_model/attack_iters_log/ --output_fn pgd8_epsilon.log.txt --eval

CUDA_VISIBLE_DEVICES=2  python3  run_reconstruct_mae.py --data_path /local/rcs/yunyun/ImageNet-Data/Attack/val/pgd_16/  --mask_ratio 0.75 --model pretrain_mae_base_patch16_224 --batch_size 16 --resume output/reconstruct_mae_v2_pretrain_model/checkpoint-109.pth --mlp_resume output/reconstruct_mae_v2_pretrain_model/mlp-checkpoint-109.pth --output_dir output/reconstruct_mae_v2_pretrain_model/attack_iters_log/ --output_fn pgd16_epsilon.log.txt --eval