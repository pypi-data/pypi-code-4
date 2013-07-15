TEMPALTE_PAY="""
<root>
    <op_code>${op_code}</op_code>
    <op_name>${op_name}</op_name>
    <op_user>${op_user}</op_user>
    <op_passwd>${op_passwd}</op_passwd>
    <op_time>${op_time}</op_time>
    <sp_id>${sp_id}</sp_id>
    <package_id>${package_id}</package_id>
    <total_num>${total_num}</total_num>
    <total_amt>${total_amt}</total_amt>
    <client_ip>${client_ip}</client_ip>
    <record_set>
        % for record in record_set:
        <%
        num, rec_bankacc, bank_type, rec_name, pay_amt, acc_type, area, city, subbank_name, desc, recv_mobile = record
        %>
        <record>
            <serial>${num}</serial>
          <rec_bankacc>${rec_bankacc}</rec_bankacc>
        <bank_type>${bank_type}</bank_type>
        <rec_name>${rec_name}</rec_name>
        <pay_amt>${pay_amt}</pay_amt>
        <acc_type>${acc_type}</acc_type>
        <area>${area}</area>
        <city>${city}</city>
        <subbank_name>${subbank_name}</subbank_name>
          <desc>${desc}</desc>
        <recv_mobile>${recv_mobile}</recv_mobile>
        </record>
        % endfor
    </record_set>
</root>"""

TEMPALTE_QUERY="""
<root>
    <op_code>${op_code}</op_code>
    <op_name>${op_name}</op_name>
<service_version>${service_version}</service_version>
    <op_user>${op_user}</op_user>
    <op_passwd>${op_passwd}</op_passwd>
    <op_time>${op_time}</op_time>
    <sp_id>${sp_id}</sp_id>
    <package_id>${package_id}</package_id>
    <client_ip>${client_ip}</client_ip>
</root>"""
