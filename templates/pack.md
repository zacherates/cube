{% for card in cards %}
![{{ card.name }}]({{ card.image_url }})
{% endfor %}

{{ notes }}


