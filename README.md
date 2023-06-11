# ChemEScribe

This is a repository for aiding with chemistry information extraction by providing methods for easily using [RxnScribe](https://github.com/thomas0809/rxnscribe), [MolDetect](https://github.com/Ozymandias314/MolDetect), and [MolScribe](https://github.com/thomas0809/MolScribe) models. 

## Installation

Run the following command to install the package and its dependencies
```
python -m pip install 'ChemEScribe @ git+https://github.com/CrystalEye42/ChemEScribe'
```

## Quick Start
Example usage:
```
from chemescribe import ChemEScribe
import cv2

model = ChemEScribe()

# Extracting molecules or reactions from a pdf
pdf_path = 'path/to/pdf'
mol_results = model.extract_mol_info_from_pdf(pdf_path)
rxn_results = model.extract_rxn_info_from_pdf(pdf_path)

# Extracting from single image
img = cv2.imread('path/to/img')
mol_results = model.extract_mol_info_from_figures([img]) 
rxn_results = model.extract_rxn_info_from_figures([img])

# Extracting from multiple images
img2 = cv2.imread('path/to/img2')
mol_results = model.extract_mol_info_from_figures([img, img2]) 
rxn_results = model.extract_rxn_info_from_figures([img, img2])

# Load specific checkpoints for various models by passing into constructor
rxnscribe_ckpt = hf_hub_download("yujieq/RxnScribe", "pix2seq_reaction_full.ckpt")
custom_model = ChemEScribe(rxnscribe_ckpt=rxnscribe_ckpt)
rxn_results = custom_model.extract_rxn_info_from_figures([img, img2])
```
