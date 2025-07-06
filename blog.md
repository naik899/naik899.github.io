---
layout: page
title: Blog
permalink: /blog/
---

# Blog

Welcome to my blog where I share insights, experiences, and technical knowledge from my journey in cloud-native architecture, AI/ML, embedded systems, and platform engineering.

## Latest Posts

{% for post in site.posts %}
<div class="blog-post-preview">
  <h3><a href="{{ post.url }}">{{ post.title }}</a></h3>
  <p class="post-meta">
    <span class="post-date">{{ post.date | date: "%B %d, %Y" }}</span>
    <span class="post-categories">
      {% for category in post.categories %}
        <span class="category-tag">{{ category }}</span>
      {% endfor %}
    </span>
  </p>
  <p class="post-excerpt">
    {{ post.excerpt | strip_html | truncatewords: 50 }}
  </p>
  <div class="post-tags">
    {% for tag in post.tags %}
      <span class="tag">{{ tag }}</span>
    {% endfor %}
  </div>
  <a href="{{ post.url }}" class="read-more">Read More →</a>
</div>
{% endfor %}

## Categories

- [Microsoft Orleans](/blog/category/microsoft-orleans/)
- [Distributed Systems](/blog/category/distributed-systems/)
- [.NET Development](/blog/category/dotnet-development/)
- [Cloud Computing](/blog/category/cloud-computing/)
- [Architecture](/blog/category/architecture/)
- [Best Practices](/blog/category/best-practices/)

## Subscribe

Stay updated with my latest posts and insights. Follow me on [LinkedIn](https://www.linkedin.com/in/naik899/) for regular updates on cloud-native architecture, AI/ML, and platform engineering.

## About the Author

I'm Ravindra Naik, a Senior Engineering Manager with 12+ years of experience building scalable systems. Currently leading cloud architecture and GenAI initiatives at Energy Exemplar, I specialize in creating robust, high-performance applications that solve real-world problems.

My expertise spans across:
- Engineering leadership and team management
- Cloud-native architecture and microservices
- Distributed systems and Microsoft Orleans
- .NET development and platform engineering
- API modernization and legacy system modernization

Feel free to reach out if you'd like to discuss any of these topics or collaborate on interesting projects! 