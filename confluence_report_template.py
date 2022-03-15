from jinja2 import Template

html = """
<h1 style="text-align: center;"><strong>{{region}}</strong></h1>
<p style="text-align: center">{{date}} - {{time_to_show}}</p>
<h2 style="text-align: center">Overall Status: <ac:structured-macro
        ac:name="status"
        ac:schema-version="1"
        ac:macro-id="ced0cd81-0b4e-44a9-a220-6cea08191aaf"
        ><ac:parameter ac:name="title">{{status.overall|upper}}</ac:parameter
        ><ac:parameter ac:name="colour">{{status.overall|upper}}</ac:parameter></ac:structured-macro
    > Health Categories: <ac:structured-macro
        ac:name="status"
        ac:schema-version="1"
        ac:macro-id="9abec0a4-e9f2-4e0b-8662-cd520a03e827"
        ><ac:parameter ac:name="title">APPLICATION</ac:parameter
        ><ac:parameter ac:name="colour">{{status.apps}}</ac:parameter></ac:structured-macro
    > <ac:structured-macro
        ac:name="status"
        ac:schema-version="1"
        ac:macro-id="28e998ba-f4fb-4aef-9449-398571feecac"
        ><ac:parameter ac:name="title">NETWORK</ac:parameter
        ><ac:parameter ac:name="colour">{{status.network}}</ac:parameter></ac:structured-macro
    > <ac:structured-macro
        ac:name="status"
        ac:schema-version="1"
        ac:macro-id="fbdee6c7-1c79-4c67-80d8-a73f9a660cdf"
        ><ac:parameter ac:name="title">SERVERS</ac:parameter
        ><ac:parameter ac:name="colour">{{status.server}}</ac:parameter></ac:structured-macro
    > <ac:structured-macro
        ac:name="status"
        ac:schema-version="1"
        ac:macro-id="fa8e9d39-b580-45b3-83b2-f8fc25f9e1b7"
        ><ac:parameter ac:name="title">JIRA INCIDENT RECORDS</ac:parameter
        ><ac:parameter ac:name="colour">{{status.jira}}</ac:parameter></ac:structured-macro
    ></h2>
<h2>Comments: All health check elements show green status at this time</h2>
<table data-layout="default" ac:local-id="4ec7e283-8922-43fc-98b7-570a590996e9">
    <colgroup>
        <col style="width: 135px" />
        <col style="width: 100px" />
        <col style="width: 450px" />
        <col style="width: 500px" />
        <col style="width: 100px" />
    </colgroup>
    <tbody>
        <tr>
            <td data-highlight-colour="#f4f5f7">
                <p><strong>Incident Type</strong></p>
            </td>
            <td data-highlight-colour="#f4f5f7">
                <p><strong>Incident Number</strong></p>
            </td>
            <td data-highlight-colour="#f4f5f7">
                <p><strong>Incident Description</strong></p>
            </td>
            <td data-highlight-colour="#f4f5f7">
                <p><strong>Impact</strong></p>
            </td>
            <td data-highlight-colour="#f4f5f7">
                <p><strong>ETA</strong></p>
            </td>
        </tr>
        {%- for key in data.keys() %}
            {%- if data[key]|length == 0:%}
            
            <tr>
                <td>
                    <p><strong>{{key}}</strong></p>
                </td>
                <td><p></p></td>
                <td><p>All {{key}} are working fine as expected.</p></td>
                <td><p>No Impact.</p></td>
                <td><p>N/A</p></td>
            </tr>
            {%- else %}
            {%- for incident in data[key]:%}
            <tr>
                {% if loop.index0 == 0 %}
                <td rowspan="{{data[key]|length}}">
                    <p><strong>{{key}}</strong></p>
                </td>
                {%- endif %}
                <td><p>{{incident['id']}}</p></td>
                <td><p>{{incident['description']}}</p></td>
                <td><p>{{incident['impact']}}</p></td>
                <td><p>{{incident['eta']}}</p></td>
            </tr>
            {%- endfor %}
            {%- endif %}
            
        {%- endfor %}
    </tbody>
</table>
<br />
"""


template = Template(html)
