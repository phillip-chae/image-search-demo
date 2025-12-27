import torch
from PIL import Image
import numpy as np
from pathlib import Path
from typing import BinaryIO

class FeatureExtractor:
        def __init__(
            self, 
            model_name: str,
            normalize: bool = True
        ):
            import timm
            from timm.data.config import resolve_model_data_config
            from timm.data.transforms_factory import create_transform
            self.normalize = normalize
            # Load the pre-trained model
            self.model = timm.create_model(
                model_name, pretrained=True, num_classes=0, global_pool="avg"
            )
            self.model.eval()

            config = resolve_model_data_config(self.model)
            # Get the preprocessing function provided by TIMM for the model
            self.transform = create_transform(**config)

        def __call__(self, image_file: str | Path | BinaryIO) -> np.ndarray:
            # Preprocess the input image
            img = Image.open(image_file).convert("RGB")  # Convert to RGB if needed
            tensor = self.transform(img).unsqueeze(0)  # type: ignore

            with torch.no_grad():
                features = self.model(tensor)

            # Extract the feature vector
            feature_vector = features.squeeze().numpy()
        
            if self.normalize:
                feature_vector = feature_vector / np.linalg.norm(feature_vector)

            return feature_vector