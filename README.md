# Pi-GPS

**This paper has been accepted by ICCV 2025.**  
**Authors:**  
Junbo Zhao$^{1}$\thanks{Equal contribution.}  
Ting Zhang$^{1}$\footnotemark[1]  
Jiayu Sun$^{1}$  
Mi Tian$^{2}$  
Hua Huang$^{1}$\thanks{Corresponding author.}  
$^1$Beijing Normal University &nbsp; $^2$TAL  

---

Code for our paper:  
[*Pi-GPS: Enhancing Geometry Problem Solving by Unleashing the Power of Diagrammatic Information*](https://arxiv.org/abs/2503.05543).

We propose **Pi-GPS**, a novel framework for geometry problem solving that leverages diagrammatic information to resolve textual ambiguities.

<div align="center">
	<img src="images/framework.png">
	<br>
	Figure 1. Framework of Pi-GPS
</div>

---

## Key Components

- **Rectifier**:  
  Utilizes multi-modal language models (MLLMs) to disambiguate text by incorporating diagrammatic context.

- **Verifier**:  
  Ensures that the refined text adheres to geometric rules, effectively reducing model hallucinations.

---

## Performance

Evaluations on benchmarks such as Geometry3K and PGPS9K demonstrate that Pi-GPS outperforms state-of-the-art neural-symbolic methods, achieving nearly a 10% improvement over previous approaches.

<div align="center">

| Category            | Method                   | Geometry3K <br> Completion | Geometry3K <br> Choice | PGPS9K <br> Completion | PGPS9K <br> Choice |
|---------------------|-------------------------|:-------------------------:|:----------------------:|:---------------------:|:------------------:|
| **MLLMs**           | Qwen-VL                 | 22.1                      | 26.7                   | 20.1                  | 23.2               |
|                     | GPT-4o                  | 34.8                      | 58.6                   | 33.3                  | 51.0               |
|                     | Claude 3.5 Sonnet       | 32.0                      | 56.4                   | 27.6                  | 45.9               |
|                     | Gemini 2                | 38.9                      | 60.7                   | 38.2                  | 56.8               |
| **Neural Methods**  | NGS                     | 35.3                      | 58.8                   | 34.1                  | 46.1               |
|                     | Geoformer               | 36.8                      | 59.3                   | 35.6                  | 47.3               |
|                     | SCA-GPS                 | -                         | 76.7                   | -                     | -                  |
|                     | GOLD*                   | -                         | 62.7                   | -                     | 60.6               |
|                     | PGPSNet-v2-S*           | 65.2                      | 76.4                   | 60.3                  | 69.2               |
|                     | LANS (Diagram GT)*      | 72.1                      | 82.3                   | 66.7                  | 74.0               |
| **Neural-symbolic** | Inter-GPS               | 43.4                      | 57.5                   | -                     | -                  |
|                     | GeoDRL                  | 57.9                      | 68.4                   | 55.6                  | 66.7               |
|                     | E-GPS                   | -                         | 67.9                   | -                     | -                  |
|                     | **Pi-GPS (ours)**       | **70.6**                  | **77.8**               | **61.4**              | **69.8**           |

</div>

---

## Prepare the Dataset

We use [Geometry3K](https://lupantech.github.io/inter-gps/#Dataset) and [PGPS9K](https://nlpr.ia.ac.cn/databases/CASIA-PGPS9K/) datasets. Download and unzip data files into `data/geometry3k` and `data/PGPS9K`.

In the Geometry3K dataset, images are stored in separate folders. To streamline processing, we have extracted them into a single unified folder by running:

```shell
python data/extract.py
```

---

## Environment Setup

- **Python version:** 3.9+
- Install required dependencies:

```shell
pip install -r requirement.txt
```

---

## Running Pi-GPS

### 1. Run with Preprocessed Data

To evaluate Pi-GPS with preprocessed data on the Geometry3K dataset:

```shell
python Solver/test.py --label final
```

### 2. Run Pi-GPS from Scratch

#### a. Text Parser

The text parser is a rule-based semantic parser that converts question text into geometry literals.

```shell
python Parser/text_parser.py
```
The pre-parsed result (`text_logic_forms_pred.json`) is already provided in `text_parser`.

#### b. Diagram Parser

The diagram parser [`PGDPNet`](https://github.com/mingliangzhang2018/PGDP) extracts geometry elements and relationships from diagrams.  
Please follow the README in PGDP for diagram parsing.  
The pre-parsed result (`PGDP.json`) is already in `diagram_parser`.

#### c. Disambiguation Module

The points recognized by the PGDP model are not displayed on the original image. To better enable the MLLM to understand the image, we first add the points to the original image:

```shell
python Disambiguation_module/addPointsToImage.py
```

To run the Disambiguation module, set your MLLM API in `Disambiguation_module/align.py` first. Different MLLMs may slightly affect the results; see our paper for details.

```shell
python Disambiguation_module/GuidedAlign.py
```
The pre-disambiguated result (`disambiguated_text_logic_forms_pred.json`) is already in `Disambiguation_module`.

#### d. Theorem Predictor

Set your reasoning LLM API in `Theorem_predictor/LLMPredict.py`:

```shell
python Theorem_predictor/LLMPredict.py
```

#### e. Solver

Finally, run the symbolic solver over the generated logic forms:

```shell
python Solver/test.py --label final_result \
  --text_logic_form_path Disambiguation_module/disambiguated_text_logic_forms_pred.json \
  --diagram_logic_form_path Parser/diagram_parser/PGDP.json \
  --predict_path Theorem_predictor/LLM_pred_seq.json
```

---

## Citation

If you find our paper or code useful, please cite:

```
@inproceedings{zhao2025pigps,
  title={Pi-GPS: Enhancing Geometry Problem Solving by Unleashing the Power of Diagrammatic Information},
  author={Junbo Zhao and Ting Zhang and Jiayu Sun and Mi Tian and Hua Huang},
  booktitle={ICCV},
  year={2025}
}
```

---

## Acknowledgements

This project is based on [Inter-GPS](https://github.com/lupantech/InterGPS), [PGDP](https://github.com/mingliangzhang2018/PGDP), and [GeoDRL](https://aclanthology.org/2023.findings-acl.850/).  
Please let us know if you encounter any issues. You can contact the first author (zhaojunbo@mail.bnu.edu.cn) or open an issue in this GitHub repo.
