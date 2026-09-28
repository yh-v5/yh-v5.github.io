---
layout: swiss
permalink: /publications/
title: works
description: Selected works by Yeong Hwan Oh, with an exhibit page for each paper.
nav: true
nav_order: 2
---

{%- assign works_n = site.data.works | size -%}

<section class="ph">
  <div class="ph-top g mono">
    <span class="l"><span class="sect">§</span> Works / Index</span>
    <span class="r">{{ works_n }} works / {{ site.data.works.first.num }}–{{ site.data.works.last.num }}</span>
  </div>
  <div class="g">
    <h1 class="ph-title">Selected<br>works</h1>
    <p class="ph-lede">
      Papers on sparse, hardware-aware hyperdimensional computing. Each title opens an exhibit page with a figure, spec sheet, abstract,
      and BibTeX.
    </p>
  </div>
</section>

<section class="sec works" aria-label="Works">
  <div class="wt-head wr g mono" aria-hidden="true">
    <span class="wr-no">No.</span>
    <span class="wr-main">Title / Authors</span>
    <span class="wr-venue">Venue</span>
    <span class="wr-year">Year</span>
    <span class="wr-links">Links</span>
  </div>
  {% bibliography -T work_row --group_by none %}
  <p class="bib-legend mono">* Equal contribution &nbsp;/&nbsp; † Corresponding author &nbsp;/&nbsp; Underline: Yeong Hwan Oh</p>
</section>
