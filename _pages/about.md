---
layout: about
title: about
permalink: /
subtitle: Combined M.S. and Ph.D. student · <a href="https://iris.skku.edu/" target="_blank">IRIS Lab</a> · Department of Electrical and Computer Engineering · <a href="https://www.skku.edu/" target="_blank">Sungkyunkwan University</a>

profile:
  align: right
  image: prof_pic.jpg
  image_circular: false
  more_info: >
    <p>📍 Suwon, Republic of Korea</p>
    <p>📧 yh991111 [at] g.skku.edu</p>

selected_papers: true
social: true

announcements:
  enabled: false
  scrollable: true
  limit: 5

latest_posts:
  enabled: false
  scrollable: true
  limit: 3
---

I am a Combined M.S. and Ph.D. student at the [IRIS Lab](https://iris.skku.edu/), Department of Electrical and Computer Engineering, [Sungkyunkwan University](https://www.skku.edu/), advised by Prof. Jong Hwan Ko.

My research centers on **sparse representations for energy-efficient on-device learning**. I work along two complementary directions:

- **Hyperdimensional computing on in-memory computing arrays.** I design algorithm–hardware co-designs that push the sparsity of HDC bound vectors above 0.99 so that the popcount stage — which dominates encoding energy — can run on simplified sparse-adder trees inside SRAM-CIM macros. Recent work targets order-of-magnitude energy reductions for edge classification while preserving accuracy.
- **Dynamic sparse training and machine unlearning at ultra-high sparsity.** At 99% sparsity, the surviving 1% of weights jointly serve both retain and forget data, making weight-only unlearning fundamentally incomplete. I am developing topology-aware unlearning methods that edit the *connectivity* of DST-trained sparse models, not just their weights, while preserving structural constraints such as constant fan-in.

Together these threads share a common premise: in modern AI systems, *what is missing* often carries as much information as *what remains*, and engineering that asymmetry is the path to deployable intelligence at the edge.

I welcome collaboration and conversation around HDC, sparse training, in-memory computing, and approximate computing for ML. The fastest way to reach me is by email.
