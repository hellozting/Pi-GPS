# Pi-GPS

🎉 **Accepted at ICCV 2025!** 🎉

> *Pi-GPS: Enhancing Geometry Problem Solving by Unleashing the Power of Diagrammatic Information*  
> [arXiv preprint](https://arxiv.org/abs/2503.05543)

---

**Authors**

| Name                     | Affiliation              | Note                      |
|--------------------------|--------------------------|---------------------------|
| Junbo Zhao  <sup>1†</sup>    | Beijing Normal University | Equal contribution        |
| Ting Zhang <sup>1†</sup>     | Beijing Normal University | Equal contribution        |
| Jiayu Sun  <sup>1</sup>      | Beijing Normal University |                           |
| Mi Tian     <sup>2</sup>     | TAL                     |                           |
| Hua Huang  <sup>1*</sup>     | Beijing Normal University | Corresponding author      |

<sup>1</sup> Beijing Normal University  
<sup>2</sup> TAL  
† Equal contribution.  
* Corresponding author. 

---

We propose **Pi-GPS**, a novel framework for geometry problem solving that leverages diagrammatic information to resolve textual ambiguities.

<div align="center">
  <img src="images/framework.png" alt="Framework of Pi-GPS" width="70%">
  <br>
  <em>Figure 1. Framework of Pi-GPS</em>
</div>

---

## 🔍 Key Components

- **Rectifier:**  
  Utilizes multi-modal language models (MLLMs) to disambiguate text by incorporating diagrammatic context.
- **Verifier:**  
  Ensures that the refined text adheres to geometric rules, effectively reducing model hallucinations.

## 🏆 Performance

Pi-GPS achieves state-of-the-art results on Geometry3K and PGPS9K, outperforming previous neural-symbolic methods by nearly 10%.

<!-- Table can keep原格式或用更简洁的展示，下面略 -->

---

## 📦 Getting Started

### 1. Prepare the Dataset

We use [Geometry3K](https://lupantech.github.io/inter-gps/#Dataset) and [PGPS9K](https://nlpr.ia.ac.cn/databases/CASIA-PGPS9K/).  
Download and unzip data files into `data/geometry3k` and `data/PGPS9K`.

In Geometry3K, images are stored in separate folders. To unify them, run:
```bash
python data/extract.py
```

### 2. Environment

- Python >= 3.9
- Install dependencies:
  ```bash
  pip install -r requirement.txt
  ```

### 3. Run Pi-GPS (Preprocessed Data)

```bash
python Solver/test.py --label final
```

### 4. Run Pi-GPS from Scratch

**Text Parser**  
```bash
python Parser/text_parser.py
```

**Diagram Parser**  
Refer to [PGDPNet](https://github.com/mingliangzhang2018/PGDP).

**Disambiguation Module**  
```bash
python Disambiguation_module/addPointsToImage.py
python Disambiguation_module/GuidedAlign.py
```
Set your MLLM API in `Disambiguation_module/align.py` before running.

**Theorem Predictor**  
```bash
python Theorem_predictor/LLMPredict.py
```

**Solver**  
```bash
python Solver/test.py --label final_result \
  --text_logic_form_path Disambiguation_module/disambiguated_text_logic_forms_pred.json \
  --diagram_logic_form_path Parser/diagram_parser/PGDP.json \
  --predict_path Theorem_predictor/LLM_pred_seq.json
```

---

## 📄 Citation

If you find our paper or code helpful, please cite:
```bibtex
@inproceedings{zhao2025pigps,
  title={Pi-GPS: Enhancing Geometry Problem Solving by Unleashing the Power of Diagrammatic Information},
  author={Junbo Zhao and Ting Zhang and Jiayu Sun and Mi Tian and Hua Huang},
  booktitle={ICCV},
  year={2025}
}
```

---

## 🙏 Acknowledgements

Our code builds upon [Inter-GPS](https://github.com/lupantech/InterGPS), [PGDP](https://github.com/mingliangzhang2018/PGDP), and [GeoDRL](https://aclanthology.org/2023.findings-acl.850/).  
For questions or suggestions, please contact the first author ([zhaojunbo@mail.bnu.edu.cn](mailto:zhaojunbo@mail.bnu.edu.cn)) or open an issue.
