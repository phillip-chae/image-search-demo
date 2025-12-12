import torch
from PIL import Image
import open_clip
from pathlib import Path
from typing import BinaryIO

# model, _, preprocess = open_clip.create_model_and_transforms('ViT-B-32', pretrained='laion2b_s34b_b79k')
# model.eval()  # model in train mode by default, impacts some models with BatchNorm or stochastic depth active
# tokenizer = open_clip.get_tokenizer('ViT-B-32')

# image = preprocess(Image.open("docs/CLIP.png")).unsqueeze(0)
# text = tokenizer(["a diagram", "a dog", "a cat"])

# with torch.no_grad(), torch.autocast("cuda"):
#     image_features = model.encode_image(image)
#     text_features = model.encode_text(text)
#     image_features /= image_features.norm(dim=-1, keepdim=True)
#     text_features /= text_features.norm(dim=-1, keepdim=True)

#     text_probs = (100.0 * image_features @ text_features.T).softmax(dim=-1)

# print("Label probs:", text_probs)  # prints: [[1., 0., 0.]]

class ClipEncoder:
    default_pretrained: dict[str, str] = {
        pair[0]: pair[1]
        for pair in open_clip.list_pretrained()
    }
    def __init__(
        self,
        model_name: str = "ViT-SO400M-16-SigLIP2-384"
    ):
        self.model, _, self.preprocess = open_clip.create_model_and_transforms(
            model_name, 
            pretrained=self.default_pretrained.get(model_name)
        )
        self.model.eval()
        self.tokenizer = open_clip.get_tokenizer(model_name)

    def encode_image(self, image: str | Path | BinaryIO) -> list[float]:
        image_tensor = self.preprocess(Image.open(image)).unsqueeze(0) # type: ignore
        with torch.no_grad(), torch.autocast("cuda"):
            image_features = self.model.encode_image(image_tensor) # type: ignore
            image_features /= image_features.norm(dim=-1, keepdim=True)
        return image_features.squeeze().tolist()
    
    def encode_text(self, texts: str | list[str]) -> list[float]:
        text_tokens = self.tokenizer(texts)
        with torch.no_grad(), torch.autocast("cuda"):
            text_features = self.model.encode_text(text_tokens) # type: ignore
            text_features /= text_features.norm(dim=-1, keepdim=True)
        return text_features.squeeze().tolist()
