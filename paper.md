# LLM-Enhanced Reinforcement Learning for Time Series Anomaly Detection

**Authors:**
- Bahareh Golchin — dept. Computer Science, Portland State University, Portland, OR, USA — bgolchin@pdx.edu
- Banafsheh Rekabdar — dept. Computer Science, Portland State University, Portland, OR, USA — rekabdar@pdx.edu
- Danielle Justo — dept. Computer Science, Smith College, Northampton, MA, USA — djusto@smith.edu

## Abstract

Detecting anomalies in time series data is crucial for finance, healthcare, sensor networks, and industrial monitoring applications. However, time series anomaly detection often suffers from sparse labels, complex temporal patterns, and costly expert annotation. We propose a unified framework that integrates Large Language Model (LLM)–based potential functions for reward shaping with reinforcement learning (RL), Variational Autoencoder (VAE)–enhanced dynamic reward scaling, and active learning with label propagation. An LSTM-based RL agent leverages LLM-derived semantic rewards to guide exploration, while VAE reconstruction errors add unsupervised anomaly signals. Active learning selects the most uncertain samples, and label propagation expands labeled data efficiently. Evaluations on Yahoo-A1 and SMD benchmarks demonstrate that our method achieves state-of-the-art detection accuracy under limited labeling budgets and operates effectively in data-constrained settings. This study highlights the promise of combining LLMs with RL and advanced unsupervised techniques for robust, scalable anomaly detection in real-world applications.[^1]

## I Introduction

Time series anomaly detection represents a critical challenge in modern data analysis, spanning applications from healthcare monitoring to industrial surveillance [1]. Traditional approaches face significant limitations when dealing with sparse labeled data, complex temporal dependencies, and real-time decision-making requirements [2]. While deep learning methods show promise, they struggle with sample efficiency and adapting to novel anomaly patterns without extensive retraining. The convergence of reinforcement learning (RL) and anomaly detection represents a paradigm shift, treating anomaly detection as an interactive learning process where agents learn optimal detection policies through environmental feedback [3].

Existing RL-based anomaly detection systems face critical challenges, including sparse reward signals, limited exploration efficiency, and difficulty incorporating domain knowledge [4, 5]. The scarcity and high cost of labeled anomaly data compound these limitations, as traditional RL methods require substantial labeled data to achieve satisfactory performance. These challenges require innovative approaches to operate effectively under data-constrained conditions while maintaining high detection accuracy [6].

The emergence of Large Language Models (LLMs) has revolutionized complex reasoning tasks across diverse domains, offering new possibilities for enhancing RL-based anomaly detection systems. Recent research demonstrates that LLMs possess remarkable capabilities in understanding temporal patterns and can effectively serve as semantic anomaly detectors by leveraging their pre-trained knowledge to assess data patterns [7].

Potential-based reward shaping (PBRS) provides a theoretically sound framework for incorporating additional reward signals without altering optimal policies [8]. This can prove to be particularly valuable in sparse reward environments where traditional RL algorithms struggle [9]. Active learning maximizes labeled sample informativeness through strategic selection, while techniques like label propagation expand labeled datasets. Variational Autoencoders (VAE) complement these approaches by providing unsupervised anomaly scoring through reconstruction error analysis [10, 11].

This work presents a novel integrated framework combining: an LSTM-based RL agent, VAE-enhanced reward mechanisms, LLM-based potential functions for semantic reward shaping, and active learning with label propagation. Our contributions include: (1) LLM-generated semantic potential functions incorporating domain knowledge without manual engineering, (2) dynamic reward scaling balancing supervised and unsupervised signals, and (3) comprehensive evaluation demonstrating superior performance on both univariate and multivariate datasets.

This comprehensive approach simultaneously addresses the sparse reward problem through LLM-based potential functions, sample efficiency through active learning, temporal dependencies through LSTM representation, and exploration-exploitation trade-offs through dynamic reward scaling. The resulting framework offers a robust solution for real-world anomaly detection where labeled data is scarce and timely, and accurate decision-making is critical.

## II Background

In what follows, we review the background related to our study.

### II-A Extrinsic and Intrinsic Rewards

In RL, rewards are categorized into extrinsic signals defined by the task designer and intrinsic signals generated internally to foster exploration [12, 13]. Extrinsic rewards drive the agent toward its primary objective, such as receiving positive feedback for correctly identifying anomalies or penalties for false alarms [8]. Although these signals provide specific feedback, they are often sparse or delayed, which can hinder effective learning. Conversely, intrinsic rewards motivate the agent to investigate unfamiliar states based on factors like novelty or prediction error, independent of external feedback [14]. For anomaly detection tasks, these intrinsic signals are crucial for guiding the agent toward unusual patterns that may not yet be labeled. By integrating both reward types, the agent effectively balances exploiting known strategies with exploring new situations, significantly enhancing both learning efficiency and adaptability [15].

### II-B Potential-Based Reward Shaping

Reward shaping accelerates learning by modifying the reward signal while strictly preserving the optimal policy. A prominent approach, Potential-Based Reward Shaping (PBRS), augments the standard reward using a potential function $\Phi(s)$ defined as:

$$
r^{\prime}(s,a,s^{\prime})=r(s,a,s^{\prime})+\gamma\Phi(s^{\prime})-\Phi(s)
\tag{1}
$$

[8]. This formulation guarantees policy invariance, ensuring the agent’s optimal behavior remains consistent with the original objective [11]. By incorporating domain heuristics or data-driven insights into $\Phi(s)$, PBRS guides the agent toward desirable states, such as identifying severe anomalies, more efficiently [16]. Consequently, the method improves convergence rates in complex environments without biasing the final learned policy [17].

### II-C Variational Autoencoder for Anomaly Detection

VAEs map input features to latent Gaussian distributions using a neural encoder-decoder architecture [18]. The model maximizes the Evidence Lower Bound (ELBO) as a tractable proxy for the intractable marginal likelihood:

$$
\mathcal{L}(\theta,\phi;x)=\mathbb{E}_{q_{\phi}(z\mid x)}\big[\log p_{\theta}(x\mid z)\big]-\mathrm{KL}\!\left(q_{\phi}(z\mid x)\,\|\,p(z)\right),
\tag{2}
$$

where the objective balances reconstruction fidelity with the Kullback–Leibler divergence between the approximate posterior $q_{\phi}(z\mid x)$ and the prior $p(z)$.

## III Proposed Method

Our proposed framework illustrates in Figure 1. The system consists of four main components: (1) an LSTM-based RL agent for sequential anomaly detection, (2) a VAE to estimate anomaly magnitude via reconstruction error with dynamic reward scaling, (3) an LLM-based semantic potential function for reward shaping, and (4) an active learning and label propagation module to minimize labeling cost.

![Fig. 1](https://arxiv.org/html/2601.02511v1/Proposed-LLM.png)

**Fig. 1:** Our proposed framework: an LSTM-based RL agent operates on sliding windows of the time series; the reward merges a VAE-based reconstruction term and an LLM potential for semantic shaping with labels supplied via active learning, producing anomaly predictions.

### III-A LSTM-based RL agent

Environment and States. Our framework models anomaly detection as a sequential decision-making process within an RL environment. The environment processes time series data sequentially, where at each time step $t$, the agent observes a state $s_{t}$, selects a binary action $a_{t}\in\{0,1\}$ (normal or anomalous), and receives a reward signal. Each episode corresponds to processing a complete time series, with the agent’s objective being to classify each time step while minimizing false detections accurately.

The state at time $t$ consists of a sliding window of $n_{\text{steps}}$ consecutive observations from the time series, $s_{t}=\{x_{t-n_{\text{steps}}+1},x_{t-n_{\text{steps}}+2},\ldots,x_{t}\}$. This enables the agent to distinguish between different action contexts; each state is augmented with an action indicator flag. This creates two possible state representations at each time step: $s_{t}^{0}=[s_{t};0]$ for predicting normal, and $s_{t}^{1}=[s_{t};1]$ for predicting anomalous.
where each augmented state $s_{t}^{a}\in\mathbb{R}^{n_{\text{steps}}\times(d+1)}$ contains both the raw sensor values and the action flag.

This dual-component design preserves essential temporal dependencies while providing the Q-network with action-specific context for learning distinct value functions. The sliding window length is set to $n_{\text{steps}}=25$, providing sufficient historical context for temporal pattern recognition while maintaining computational efficiency.

Extrinsic Reward. The extrinsic reward mechanism provides direct feedback on the agent’s classification decisions, guiding learning through immediate reinforcement based on prediction accuracy. At each time step, the agent selects a binary action $a_{t}\in\{0,1\}$ representing predict normal or predict anomaly, respectively, and receives reward feedback based on the ground truth label $y_{t}$.

Classification-Based Reward Structure. The primary extrinsic reward $R_{1}(s_{t},a_{t})$ follows a confusion matrix-based formulation, giving $+5$ for true positives, $+1$ for true negatives, $-1$ for false positives, and $-5$ for false negatives ($R_{1}(s_{t},a_{t})\in\{5,1,-1,-5\}$).

### III-B VAE-Enhanced Reward Augmentation

To complement the classification feedback, we incorporate reconstruction error from a VAE trained exclusively on normal patterns. The VAE provides an unsupervised anomaly score that captures deviations from learned normal behavior:

$$
R_{2}(s_{t})=\mathrm{MSE}(x_{t},\hat{x}_{t})=\frac{1}{n}\sum_{i=1}^{n}(x_{t,i}-\hat{x}_{t,i})^{2},
\tag{3}
$$

where $x_{t}$ represents the current window, $\hat{x}_{t}$ is its VAE reconstruction, and $n$ is the window dimensionality. Higher reconstruction errors indicate greater deviation from normal patterns, providing additional evidence for anomaly presence.

Dynamic Reward Integration. The final extrinsic reward combines classification accuracy with reconstruction-based guidance through a dynamically scaled formulation:

$$
R_{\text{total}}(s_{t},a_{t})=R_{1}(s_{t},a_{t})+\lambda(t)\cdot R_{2}(s_{t}),
\tag{4}
$$

where $\lambda(t)$ is a time-varying coefficient that balances supervised classification feedback ($R_{1}$) with unsupervised anomaly scoring ($R_{2}$). The coefficient $\lambda(t)$ is updated after each episode using proportional control:

$$
\lambda_{t+1}=\mathrm{clip}\left(\lambda_{t}+\alpha\left(R_{\mathrm{target}}-R_{\mathrm{episode}}\right),\lambda_{\mathrm{min}},\lambda_{\mathrm{max}}\right),
\tag{5}
$$

where $\alpha$ is the adjustment rate, $R_{\mathrm{target}}$ is the desired episode reward, and $R_{\mathrm{episode}}$ is the actual episode reward. If performance drops ($R_{\mathrm{episode}}<R_{\mathrm{target}}$), $\lambda$ increases to give more weight to the VAE anomaly signal; if performance improves, $\lambda$ decreases to focus more on classification. Bounds $[\lambda_{\mathrm{min}},\lambda_{\mathrm{max}}]$ keep updates stable.

### III-C LLM-Based Potential Function

To enrich the reward signal with semantic context, we introduce a potential-based shaping term derived from an LLM. This component leverages the LLM’s ability to assess complex temporal patterns and provide an interpretable anomaly severity score, which serves as the potential function $\phi(s)$ in the reward shaping framework as shown in Equation (1).

Severity Scoring via LLM. For a given state $s_{t}$, represented as a sliding window of $n_{\text{steps}}$ consecutive sensor readings, the values are formatted into a structured prompt and provided to the LLM (e.g., models GPT-3.5, Llama-3.2-3B, and Phi-2). The model is instructed to output a single JSON object: {”severity”: v}. Where $v\in[0,1]$ quantifies the likelihood of the current window containing an anomaly, with $0$ representing “certainly normal” and $1$ representing “certainly anomalous”. This output is parsed to extract the scalar potential $\phi(s_{t})=v$.

Few-Shot Prompt Design. The LLM prompt shows a few example sensor readings with their severity scores to help it give consistent and accurate results. For instance:

- Sensor readings: [0.0, 0.0, 0.0, 0.0, ...] $\rightarrow$ {"severity": 0.00}
- Sensor readings: [0.0, 0.0, 0.0, 5.0, 5.0, ...] $\rightarrow$ {"severity": 0.75}

These examples act as anchors, which help the LLM to map diverse patterns to a bounded and meaningful anomaly severity scale. The prompt structure includes system-level instructions enforcing JSON-only output to prevent parsing errors and ensure reliable extraction of severity scores.

Integration into Reward Shaping. Recall Equation (1) (i.e., $r^{\prime}(s_{t},a_{t})=r(s_{t},a_{t})+\gamma\,\phi(s_{t+1})-\phi(s_{t})$). In our proposed method, we define: 1) $r(s_{t},a_{t})$ as the extrinsic reward from classification and VAE-based penalties, and 2) $\phi(s)$ as the LLM-generated potential. Next, similar to the literature, we define $\gamma$ as the discount factor. This approach preserves the optimal policy while providing a richer training signal that guides the agent toward states with higher anomaly likelihood.

Semantic Context Enhancement. Unlike traditional methods that only look for statistical patterns in data, the LLM potential function uses advanced reasoning to understand time-based patterns. The LLM can identify complex, unusual behaviors like sudden jumps, irregular changes, or subtle shifts in trends that purely numerical methods might miss. By combining basic numerical features with the LLM’s high-level understanding, the potential function connects statistical anomaly detection with contextual reasoning. This helps the RL agent work more efficiently by better exploring and using informative areas of the data space.

### III-D Active Learning Integration

To reduce annotation effort while maintaining strong detection performance, the framework integrates an AL module that works alongside the RL agent. This module selects the most informative samples for human labeling and uses semi-supervised learning to spread labels to similar unlabeled instances. At the end of each episode, uncertainty is measured by the margin $\mathrm{Margin}(s)=\left|Q(s,a_{0})-Q(s,a_{1})\right|$,
and the top $N_{\mathrm{AL}}$ states with the smallest margins are sent for manual annotation. A label propagation step then assigns pseudo-labels to additional unlabeled samples based on similarity weights $w_{ij}$, typically computed with a Gaussian kernel in feature space. The $K_{\mathrm{LP}}$ most confident pseudo-labels are added to the labeled set, further improving the training signal while limiting human labeling effort.

## IV Experiments

This section describes our experiments. We start by describing the datasets and then address three key research questions: (Q1) Does using LLMs for potential-based reward shaping perform better than existing methods? (Q2) Which LLM (GPT 3.5, Llama-3, Phi-2) works best in our anomaly detection approach and why? (Q3) How does our method perform on univariate versus multivariate time series datasets?

### IV-A Datasets

We evaluate our framework on two widely used benchmarks: Yahoo-A1 (67 univariate series from real Yahoo website traffic) and SMD (28 multivariate series with 38 sensors from server machines). Yahoo-A1 contains hourly collected data with labeled anomaly points, while SMD includes 10 days of sensor data with normal patterns in the first 5 days and random anomalies in the last 5 days [19, 20]. Table I summarizes the key dataset statistics.

**TABLE I:** Key Statistics for Yahoo-A1 and SMD

| Benchmark | # series | # dims | Anomaly % |
| --- | ---: | ---: | ---: |
| Yahoo-A1 | 67 | 1 | 1.76% |
| SMD | 28 | 38 | 4.16% |

### IV-B Results and Discussions

To answer Q1, Table II (left) summarizes performance on Yahoo A1. Our method with Llama-3 achieves an F1 of 0.7413 with precision/recall of 0.6051/0.9565, essentially on par with the strongest non-LLM baseline (CARLA: 0.7233 F1). Compared with earlier deep baselines such as TimesNet (0.5135 F1) and TranAD (0.5654 F1), the gain is sizeable. The high recall indicates the LLM-shaped potential guides the agent to consistently surface true anomalies, while maintaining moderate precision. In contrast, the GPT-3.5 variant attains very high recall (0.9130) but extremely low precision (0.0742), leading to a poor F1 of 0.1372. This reflects an over-eager anomaly prior to GPT that over-flags peaks. The Phi-2 variant shows the opposite behavior, 0.6666 precision but only 0.4761 recall, suggesting a conservative prior that misses many positives; its F1 is 0.5555.

On SMD (right side of the Table II), Llama-3 again provides the best trade-off, reaching an F1 of 0.5300 with precision/recall of 0.3813/0.8685. This outperforms CARLA (0.5114 F1) and other non-LLM baselines. The Industrial SMD series contains strong seasonality and gradual drifts; the Llama-shaped potential appears calibrated enough to keep recall high without flooding detections. GPT-3.5 performs better than on Yahoo (precision/recall 0.5370/0.4061; F1 = 0.4625), but it still underperforms Llama-3, likely because its anomaly prior is too permissive. Phi-2 is highly precise on SMD (0.8461) yet recalls only 0.2541 of anomalies (F1 0.3908), again consistent with a cautious prior.

To answer Q2, we identify three practical reasons. First, Llama-3 follows instructions well and produces smooth severity scores within the required $[0,1]$ range, creating balanced signals that work effectively for potential-based reward shaping. Second, Llama-3 shows better pattern recognition compared to other models. GPT often overreacts to minor changes and assigns high scores too broadly.
An example of this phenomenon is illustrated in
Figure 2, where Llama-3 properly identifies significant changes and outliers without being overly sensitive to normal variations. Third, Llama-3 produces more consistent outputs across different time windows, resulting in less noisy shaped rewards and helping the RL agent learn clearer decision boundaries.

![Fig. 2](https://arxiv.org/html/2601.02511v1/SMD_Llama.png)

**Fig. 2:** SMD anomaly detection — Llama. Colors: blue = original signal; green = true (ground-truth) anomalies; red = detected anomalies. Panels: top-left shows ground truth over the signal; top-right shows ground truth + detected anomalies; bottom-left and bottom-right are two zoomed-in regions.

To answer Q3, Yahoo A1 is a simple dataset where each time series has only one variable and anomalies are typically sudden spikes or shifts in the mean value. These types of anomalies are easy to detect using short time windows because an LLM can identify obvious patterns like spikes or jumps, leading to good detection performance. In contrast, SMD is a complex multivariate dataset with many related sensors per machine that show seasonal patterns and gradual changes over time. In SMD, real anomalies usually occur when multiple sensors change together or when deviations continue for extended periods, making individual sensors appear normal despite the overall anomaly. This complexity makes detection more difficult because methods need to understand relationships between different sensors and track changes over time, or they will either miss real anomalies or incorrectly flag normal seasonal variations. Our approach computes LLM severity scores for each window and uses them for reward shaping, which works well for Yahoo’s simple, single-variable anomalies but struggles with SMD’s complex multi-sensor patterns unless the model can capture cross-sensor relationships and temporal consistency.

**TABLE II:** Comparison of our framework on two benchmark time series datasets: Yahoo A1 and SMD

| Model | Yahoo A1 Prec | Yahoo A1 Rec | Yahoo A1 F1 | SMD Prec | SMD Rec | SMD F1 |
| --- | :---: | :---: | :---: | :---: | :---: | :---: |
| THOC [21] | 0.1495 | 0.8326 | 0.2534 | 0.0997 | 0.5307 | 0.1679 |
| TranAD [22] | 0.4185 | 0.8712 | 0.5654 | 0.2649 | 0.5661 | 0.3609 |
| TS2Vec [23] | 0.3929 | 0.6305 | 0.4841 | 0.1033 | 0.5295 | 0.1728 |
| DCdetector [24] | 0.0598 | 0.9434 | 0.1124 | 0.0432 | 0.9967 | 0.0828 |
| TimesNet [25] | 0.3808 | 0.7883 | 0.5135 | 0.2450 | 0.5474 | 0.3385 |
| CARLA [26] | 0.5747 | 0.9755 | 0.7233 | 0.4276 | 0.6362 | 0.5114 |
| Proposed Method + GPT-3.5 | 0.0742 | 0.9130 | 0.1372 | 0.5370 | 0.4061 | 0.4625 |
| Proposed Method + Llama-3.2-3B | 0.6051 | 0.9565 | 0.7413 | 0.3813 | 0.8685 | 0.5300 |
| Proposed Method + Phi-2 | 0.6666 | 0.4761 | 0.5555 | 0.8461 | 0.2541 | 0.3908 |

## V Conclusion

This study presents a novel framework integrating LLM-based potential functions with reinforcement learning for time series anomaly detection, addressing sparse rewards and limited labeled data challenges. Our approach demonstrates that semantic reward shaping through LLMs, particularly Llama-3, effectively guides RL agents while maintaining policy invariance, with VAE-enhanced dynamic reward scaling and active learning achieving competitive performance on Yahoo-A1 and SMD datasets. Experimental results reveal distinct LLM behavioral patterns in anomaly assessment, with Llama-3 providing optimal precision-recall balance across univariate and multivariate scenarios. The framework’s effectiveness under data-constrained conditions makes it valuable for real-world applications, with future work exploring complex multivariate relationships and additional LLM architectures.

## Acknowledgment

This material is based on work supported by the National Science Foundation under grant no. 2244551.

## References

- [1] B. Kim, M. A. Alawami, E. Kim, S. Oh, J. Park, and H. Kim (2023) A comparative study of time series anomaly detection models for industrial control systems. Sensors 23 (3), pp. 1310.
- [2] M. Zhang, Y. Sun, and F. Liang (2023) Sparse deep learning for time series data: theory and applications. In Proc. 37th Conf. Neural Inf. Process. Syst. (NeurIPS 2023), Poster,
- [3] H. Bastani, O. Bastani, and W. S. P. Sinchaisri (2025) Improving human sequential decision-making with reinforcement learning. Management Science. Note: Articles in Advance
- [4] L. Kweider, M. A. Kassem, and U. Sandouk (2024) Anomalous state sequence modeling to enhance safety in reinforcement learning. IEEE Access 12, pp. 157140–157148. External Links: [Document](https://dx.doi.org/10.1109/ACCESS.2024.3486549)
- [5] X. Chen, R. Xiao, Z. Zeng, Z. Qiu, S. Zhang, and X. Du (2024) Semi-supervised anomaly detection via adaptive reinforcement learning-enabled method with causal inference for sensor signals. External Links: 2405.06925
- [6] F. Khanizadeh, A. Ettefaghian, G. Wilson, A. Shirazibeheshti, T. Radwan, and C. Luca (2025) Smart data-driven medical decisions through collective and individual anomaly detection in healthcare time series. Int. J. Med. Informatics 194, pp. 105696.
- [7] S. Bhambri, A. Bhattacharjee, D. Kalwar, L. Guan, H. Liu, and S. Kambhampati (2024) Extracting heuristics from large language models for reward shaping in reinforcement learning. External Links: 2405.15194
- [8] A. Y. Ng, D. Harada, and S. J. Russell (1999) Policy invariance under reward transformations: theory and application to reward shaping. In Proc. 16th Int. Conf. Mach. Learn. (ICML), pp. 278–287.
- [9] G. C. Forbes, N. Gupta, L. Villalobos-Arias, C. M. Potts, A. Jhala, and D. L. Roberts (2024) Potential-based reward shaping for intrinsic motivation. In Proc. 23rd Int. Conf. Autonomous Agents and Multiagent Systems (AAMAS), Auckland, New Zealand, pp. 589–597.
- [10] B. Golchin and B. Rekabdar (2024) Anomaly detection in time series data using reinforcement learning, variational autoencoder, and active learning. In Proc. Conf. AI, Science, Engineering, and Technology (AIxSET), Laguna Hills, CA, USA, pp. 1–8.
- [11] E. Wiewiora (2003) Potential-based shaping and q-value initialization are equivalent. J. Artif. Intell. Res. 19, pp. 205–208.
- [12] R. S. Sutton and A. G. Barto (2018) Reinforcement learning: an introduction. 2 edition, MIT Press, Cambridge, MA, USA.
- [13] N. Chentanez, A. G. Barto, and S. P. Singh (2005) Intrinsically motivated reinforcement learning. In Advances in Neural Information Processing Systems 17, pp. 1281–1288.
- [14] A. G. Barto (2013) Intrinsic motivation and reinforcement learning. In Intrinsic Motivation and Reinforcement Learning, G. Baldassarre and M. Mirolli (Eds.), pp. 17–47.
- [15] D. Pathak, P. Agrawal, A. A. Efros, and T. Darrell (2017) Curiosity-driven exploration by self-supervised prediction. In Proc. IEEE Conf. Comput. Vis. Pattern Recognit. (CVPR), pp. 2778–2787.
- [16] S. Devlin and D. Kudenko (2012) Dynamic potential-based reward shaping. In Proc. 11th Int. Conf. Autonomous Agents and Multiagent Systems (AAMAS), pp. 433–440.
- [17] M. Grzes (2017) Reward shaping in episodic reinforcement learning. In Proc. 16th Int. Conf. Autonomous Agents and MultiAgent Systems (AAMAS), pp. 565–573.
- [18] E. A. Elaziz, R. Fathalla, and M. Shaheen (2023) Deep reinforcement learning for data-efficient weakly supervised business process anomaly detection. Journal of Big Data 10 (1), pp. 33.
- [19] N. Laptev, B. Y., and S. Amizadeh (2015) A benchmark dataset for time series anomaly detection (Website) Note: Yahoo! Research Blog External Links: [Link](https://yahooresearch.tumblr.com/post/114590420346/a-benchmark-dataset-for-time-series-anomaly)
- [20] Y. Su, Y. Zhao, C. Niu, R. Liu, W. Sun, and D. Pei (2019) Robust anomaly detection for multivariate time series via stochastic recurrent neural network. In Proc. ACM SIGKDD Int. Conf. Knowl. Discov. Data Min. (KDD), pp. 2828–2837.
- [21] L. Shen, Z. Li, and J. T. Kwok (2020) Time-series anomaly detection using temporal hierarchical one-class network. In Advances in Neural Information Processing Systems 33 (NeurIPS), pp. 13016–13026.
- [22] S. Tuli, G. Casale, and N. R. Jennings (2022) TranAD: deep transformer networks for anomaly detection in multivariate time series data. Proc. VLDB Endow. 15 (6), pp. 1201–1214.
- [23] Z. Yue, Y. Wang, J. Duan, T. Yang, C. Huang, Y. Tong, and B. Xu (2022) TS2Vec: towards universal representation of time series. In Proc. AAAI Conf. Artif. Intell. (AAAI), pp. 8980–8987.
- [24] Y. Yang, C. Zhang, T. Zhou, Q. Wen, and L. Sun (2023) DCdetector: dual attention contrastive representation learning for time series anomaly detection. In Proc. 29th ACM SIGKDD Int. Conf. Knowl. Discov. Data Min. (KDD), Long Beach, CA, USA.
- [25] H. Wu, T. Hu, Y. Liu, H. Zhou, J. Wang, and M. Long (2023) TimesNet: temporal 2d-variation modeling for general time series analysis. In Int. Conf. Learn. Representations (ICLR),
- [26] Z. Z. Darban, G. I. Webb, S. Pan, C. C. Aggarwal, and M. Soleimani (2025) Deep learning for time series anomaly detection: a survey. ACM Comput. Surv. 57 (1), pp. Article 15, 1–42.

---

[^1]: Code is available at [GitHub Repository](https://github.com/baharehgl/Reward-Shaping-LLM/tree/main).
