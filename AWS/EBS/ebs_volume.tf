{%- for vol in volumes %}
resource "aws_ebs_volume" "example_{{vol.volume}}" {
  availability_zone = "{{vol.availability_zone}}"
  encrypted         = {{vol.encrypted | lower}}
  size              = {{vol.size}}
  type              = "{{vol.type}}"

  tags = {
   {%- for k,v in vol.tags.items() %}
    {{ k }} = "{{ v }}"
    {%- endfor %}
  }
}{%- endfor%}
{%- for vol in volumes %}
output "ebs_volume_{{vol.volume}}" {
    value = aws_ebs_volume.example_{{vol.volume}}.id
}
{%- endfor%}