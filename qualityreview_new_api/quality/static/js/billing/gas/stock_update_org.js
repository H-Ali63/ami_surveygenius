function insert(){

    var brand=document.getElementById("brand_type").value
    var variant=document.getElementById("variant").value
    var variant_type=document.getElementById("variant_type").value
    var packing_type=document.getElementById("packing_type").value
    var noBoxes=document.getElementById("no_boxes").value
    var quantity=document.getElementById("quantity").value
    var receiving_date=document.getElementById("receiving_date").value
    var location_id=document.getElementById("location_id").value
    var is_sample = document.getElementById("is_sample").value

    if(brand!="default" && variant!="default" && variant_type!="default" && noBoxes!="" && quantity!="" && receiving_date!="" && location_id!=""){
        var token=document.getElementById("tk").getAttribute("data-token")
        var form_data = new FormData()
        console.log(document.getElementById("bill_upload").files.length,"<<<files")
        var file_upload = null
        if(document.getElementById("bill_upload").files.length!=0){
            file_upload = document.getElementById("bill_upload").files[0]
        }else{
            file_upload=null
        }

        form_data.append("file",file_upload)
        request_obj = {
        "brand":brand,
        "variant":variant,
        "variant_type":variant_type,
        "packing_type":packing_type,
        "noBoxes":noBoxes,
        "quantity":quantity,
        "receiving_date":receiving_date,
        "location_id":location_id,
	"is_sample":is_sample

        }
        console.log(request_obj)
        form_data.append("req",JSON.stringify(request_obj))
        $.ajax({
        headers: { "X-CSRFToken": token },
        type:"POST",
        url:"http://pnndsrvctvt.com:8000/billing/gas/api/add/",
        data:form_data,
        processData: false,
        contentType: false,
        success:function(response){
            console.log(response)
            document.getElementById("stock_records").innerHTML+="<tr style='font-size: 13px;font-weight: 500;word-wrap: break-word;text-align: center;'><td style='border: 1px solid black;'>"+response.id+"</td><td style='border: 1px solid black;'>"+brand+"</td><td style='border: 1px solid black;'>"+variant+"</td><td style='border: 1px solid black;'>"+variant_type+"</td><td style='border: 1px solid black;'>"+packing_type+"</td><td style='border: 1px solid black;'>"+noBoxes+"</td>"+
            "<td style='border: 1px solid black;'>"+quantity+"</td><td style='border: 1px solid black;'>"+(noBoxes*quantity)+"</td><td style='border: 1px solid black;'>"+receiving_date+"</td><td style='border: 1px solid black;'>"+location_id+"</td><td style='border: 1px solid black;'>"+response.created_at+"</td>"+
            "<td style='border: 1px solid black;'>"+response.employee_id+"</td><td style='border: 1px solid black;'><a href='pnndsrvctvt.com:8000/media/"+response.file_path+"' download='pnndsrvctvt.com:8000/media/"+response.file_path+"'>download</a></td></tr>"
        }
        })
    }else{
        alert("Please fill all details ! ")
    }



}

console.log("stockkk details")
function brand_stock_details(event,id){
    console.log("===")
    var brand_id=null
    var city=null
    if(event.id=="brand_type"  && document.getElementById(id).value!="default"){
        brand_id = event.value
        city = document.getElementById(id).value
    }else if(event.id=="cities" && document.getElementById(id).value!="default"){
        city = event.value
        brand_id = document.getElementById(id).value
    }
    if(brand_id!=null && city!=null){
        var token=document.getElementById("tk").getAttribute("data-token")
        request_obj = {
            "brand_id":brand_id,
            "city":city
        }
        $.ajax({
        headers: { "X-CSRFToken": token },
        type:"GET",
        url:"http://pnndsrvctvt.com:8000/billing/gas/api/brand/stock_details",
        data:request_obj,
        data_type:"json",
        contentType: "application/json",
        success:function(response){
            console.log(response)
            if(response.status==200){
		if(response.total_stock_sample==null){
                    document.getElementById("samples_received").value = 0
                }else{
                    document.getElementById("samples_received").value = response.total_stock_sample
                }
    
                if(response.total_stock_kit_test==null){
                    document.getElementById("kits_received").value = 0
                }else{
                    document.getElementById("kits_received").value = response.total_stock_kit_test
                }
                //document.getElementById("samples_received").value = response.total_stock_sample
                //document.getElementById("kits_received").value = response.total_stock_kit_test
            }
        }
        })
    }


}


function calcaculate_quantity(event){
    document.getElementById("kit_shortfall").value=""
    document.getElementById("sample_shortfall").value=""
    var order_quantity = event.value
    var samples_received = document.getElementById("samples_received").value
    var kits_received = document.getElementById("kits_received").value
    var sample_shortfall = parseInt(samples_received) - parseInt(order_quantity)
    var kit_shortfall = parseInt(kits_received) - parseInt(order_quantity)
    document.getElementById("sample_shortfall").value=sample_shortfall
    document.getElementById("kit_shortfall").value=kit_shortfall
    console.log(document.getElementById("kit_shortfall").value)
}


function addConsumption(id){


    var consumption_data = document.getElementsByClassName("consumption_from_to")
    var total_samples_distributes=0
    var total_samples_to_kits=0
    var kits_received = document.getElementById("kits_received").value
    for(var i=0;i<consumption_data.length;i++){
        console.log(consumption_data[i].getElementsByClassName("from")[0].value)
        if(consumption_data[i].getElementsByClassName('from')[0].value!="" && consumption_data[i].getElementsByClassName('to')[0].value!="" && consumption_data[i].getElementsByClassName('consume_quantity')[0].value){
            var from_date = consumption_data[i].getElementsByClassName('from')[0].value
            var to_date = consumption_data[i].getElementsByClassName('to')[0].value
            var used_consumption = consumption_data[i].getElementsByClassName('consume_quantity')[0].value

            console.log("values::",from_date,"==",to_date,"==",used_consumption)
            total_samples_distributes=total_samples_distributes+parseInt(used_consumption)
        }

    }



    document.getElementById("total_samples_distributes").value=total_samples_distributes
    document.getElementById("total_samples_to_kits").value= parseInt(kits_received) - parseInt(total_samples_distributes) //total_samples_to_kits

}

function add_elem(id){
    $('#'+id).append("<div class='consumption_from_to' style='margin-top:10px;'>"+
        "<span>Consumption from </span><input type='date' class='from'  />"+
        "<span>Consumption to </span><input type='date' class='to' />"+
        "<span>Consumption</span><input type='number' class='consume_quantity' value=''  onkeyup=addConsumption('consumption_div') /></div>")

}


function consumption_insert(event){

    console.log("consumption_insert")
    var consumption_request={}
    var brand = document.getElementById("brand_type").value
    var activity = document.getElementById("activity").value
    var city = document.getElementById("cities").value
    var start_date = document.getElementById("receiving_date").value
    var order_quantity = document.getElementById("order_quantity").value
    var samples_received = document.getElementById("samples_received").value
    var kits_received = document.getElementById("kits_received").value
    var sample_shortfall = document.getElementById("sample_shortfall").value
    var kit_shortfall = document.getElementById("kit_shortfall").value

    consumption_request["brand"]=brand
    consumption_request["activity"]=activity
    consumption_request["city"]=city
    consumption_request["start_date"]=start_date
    consumption_request["order_quantity"]=order_quantity
    consumption_request["kits_received"]=kits_received
    consumption_request["samples_received"]=samples_received
    consumption_request["sample_shortfall"]=sample_shortfall
    consumption_request["kit_shortfall"]=kit_shortfall
    consumption_request["consumptions"]=[]


    var consumption_data = document.getElementsByClassName("consumption_from_to")
    for(var i=0;i<consumption_data.length;i++){
        console.log(consumption_data[i].getElementsByClassName("from")[0].value)
        if(consumption_data[i].getElementsByClassName('from')[0].value!="" && consumption_data[i].getElementsByClassName('to')[0].value!="" && consumption_data[i].getElementsByClassName('consume_quantity')[0].value){
            var from_date = consumption_data[i].getElementsByClassName('from')[0].value
            var to_date = consumption_data[i].getElementsByClassName('to')[0].value
            var used_consumption = consumption_data[i].getElementsByClassName('consume_quantity')[0].value
            console.log("values::",from_date,"==",to_date,"==",used_consumption)
            total_samples_distributes=total_samples_distributes+parseInt(used_consumption)
            consumption_request["consumptions"].push({
            "from":from_date,
            "to":to_date,
            "consumption_quantity":used_consumption
            })
        }

    }

    var total_samples_distributes = document.getElementById("total_samples_distributes").value
    var total_samples_to_kits = document.getElementById("total_samples_to_kits").value

    consumption_request["total_samples_distributes"]=total_samples_distributes
    consumption_request["total_samples_to_kits"]=total_samples_to_kits

    console.log(consumption_request,"<<<consumption")
    var token=document.getElementById("tk").getAttribute("data-token")
    var form_data = new FormData()
    console.log(document.getElementById("consumption_bill_upload").files.length,"<<<files")
    var file_upload = null
    if(document.getElementById("consumption_bill_upload").files.length!=0){
        file_upload = document.getElementById("consumption_bill_upload").files[0]
    }else{
        file_upload=null
    }

    form_data.append("file",file_upload)
    form_data.append("req",JSON.stringify(consumption_request))
    if(consumption_request["consumptions"].length>0){
        $.ajax({
            headers: { "X-CSRFToken": token },
            type:"POST",
            url:"http://pnndsrvctvt.com:8000/billing/gas/api/consumption/add/",
            data:form_data,
            processData: false,
            contentType: false,
            success:function(response){
                console.log(response)
		location.reload()
            }
        })
    }else{
        alert("please fill proper details ")
    }

}



function get_consumption_details(consumption_id){
console.log("get_compution_details")
var token=document.getElementById("tk").getAttribute("data-token")
    $.ajax({
        headers: { "X-CSRFToken": token },
            type:"GET",
            url:"http://pnndsrvctvt.com:8000/billing/gas/api/consumption_data/id/",
            data:{
                id:consumption_id,
            },
            data_type:"json",
            contentType: "application/json",
            success:function(response){
//                console.log(response,"--------")
                console.log("===========",response)
                document.getElementById("myModal").style['display']="block"
                document.getElementById("brand_model").innerHTML=response["consumption_data"][0]["fields"]["brand"]
                document.getElementById("activity_model").innerHTML=response["consumption_data"][0]["fields"]["activity"]
                document.getElementById("start_date_model").innerHTML=response["consumption_data"][0]["fields"]["start_date"]
                document.getElementById("order_quantity_model").innerHTML=response["consumption_data"][0]["fields"]["order_quantity"]
                document.getElementById("total_samples_distributed_model").innerHTML=response["consumption_data"][0]["fields"]["total_samples_distributed"]
                document.getElementById("total_samples_distributed_per_kit_model").innerHTML=response["consumption_data"][0]["fields"]["total_samples_distributed_per_kit"]
                document.getElementById("kits_received_model").innerHTML=response["consumption_data"][0]["fields"]["kits_received"]
                document.getElementById("samples_received_model").innerHTML=response["consumption_data"][0]["fields"]["sample_received"]
                document.getElementById("kits_shortfall_model").innerHTML=response["consumption_data"][0]["fields"]["kits_shortfall"]
                document.getElementById("samples_shortfall_model").innerHTML=response["consumption_data"][0]["fields"]["sample_shortfall"]

                document.getElementById("consumption_details_model").innerHTML=""
                $('#consumption_details_model').append(
                            "<tr><td style='border: 1px solid black;'>From Date</td>"+
                            "<td style='border: 1px solid black;'>To Date</td>"+
                            "<td style='border: 1px solid black;'>Consumption Quantity</td></tr>"
                    )
                for(var i=0;i<response["consumption_data_details"].length;i++){
                    $('#consumption_details_model').append(
                            "<tr><td style='border: 1px solid black;'>"+response["consumption_data_details"][i]["fields"]["from_date"]+"</td>"+
                            "<td style='border: 1px solid black;'>"+response["consumption_data_details"][i]["fields"]["to_date"]+"</td>"+
                            "<td style='border: 1px solid black;'>"+response["consumption_data_details"][i]["fields"]["consumption_quantity"]+"</td></tr>"
                    )
                }


            }


    })

}


//HUL Starts
function hul_add_quantity(){
    console.log("hul quantity insert")
    var activity_name = document.getElementById("add_activity").value
    var order_quantity =document.getElementById("add_order_quantity").value
    var buffer_order_percent =document.getElementById("buffer_order_percent").value
    var activity_location =document.getElementById("activity_location").value

    if(activity_name!="" && order_quantity!=""){
        var token=document.getElementById("tk").getAttribute("data-token")

        $.ajax({
            headers: { "X-CSRFToken": token },
            type:"POST",
            url:"http://pnndsrvctvt.com:8000/billing/hul/api/add/quantity/",
            data:JSON.stringify({
                "activity":activity_name,
                "order_quantity":order_quantity,
		"buffer_order_percent":buffer_order_percent,
		"activity_location":activity_location
            }),
            data_type:"json",
            success:function(response){
                console.log(response)
//                document.location.reload(true)
		document.getElementById("displayModal").style["display"]="block"
                document.getElementById("added_activity_name").innerHTML=response["activity_name"]
                document.getElementById("added_quantity").innerHTML=response["activity_quantity"]
                document.getElementById("added_buffer_percent").innerHTML=response["activity_buffer_percent"]
		document.getElementById("added_location").innerHTML=response["activity_location"]
                setTimeout(()=>{document.location.reload(true)},5000)
            }
        })
    }
}

function select_order_quantity(evt){
    console.log("onclick")
    document.getElementById("location").value = evt.value.split("&-&")[3]
    document.getElementById("order_quantity").value = evt.value.split("&-&")[2]
    document.getElementById("buffer_activity_order").value = evt.value.split("&-&")[1]
}

function calculate_quantity(evt, id){
    var total_quantity = evt.value * document.getElementById(id).value
    document.getElementById("total_received_quantity").value = total_quantity
}

function hul_stock_insert(){
    console.log("hul_insert")
    var activity_id = document.getElementById("activity_name").value.split("&-&")[0]
//    var order_quantity =document.getElementById("order_quantity").value
    var receipt_number =document.getElementById("receipt_no").value
    var variant =document.getElementById("variant").value
    var type_of_material =document.getElementById("type_of_material").value
    var number_of_boxes =document.getElementById("no_of_boxes").value
    var quantity_per_box =document.getElementById("quantity_per_box").value
    var total_quantity_received =document.getElementById("total_received_quantity").value
    var material_receiving_date = document.getElementById("receiving_date").value
    var location = document.getElementById("location").value
    var client_name = document.getElementById("client_name").value
    var receiver = document.getElementById("receiver").value
//    var photo_copy = document.getElementById("is_sample").value
//    var material_receiving_date = document.getElementById("is_sample").value

    if(activity_id!="default" && receipt_number!="default" && variant!="default" && type_of_material!="" && number_of_boxes!="" && quantity_per_box!="" &&
    total_quantity_received!="" && material_receiving_date!="" && location!="" && client_name!="" && receiver!="" && document.getElementById("bill_upload").files.length!=0){

        var token=document.getElementById("tk").getAttribute("data-token")
        var form_data = new FormData()
        var file_upload = null

        file_upload = document.getElementById("bill_upload").files[0]

        form_data.append("file",file_upload)
        request_obj = {
        "activity_id":activity_id,
//        "order_quantity":order_quantity,
        "receipt_number":receipt_number,
        "variant":variant,
        "type_of_material":type_of_material,
        "number_of_boxes":number_of_boxes,
        "quantity_per_box":quantity_per_box,
        "total_quantity_received":total_quantity_received,
        "material_receiving_date":material_receiving_date,
        "location":location,
        "client_name":client_name,
        "receiver":receiver
//        "material_receiving_date":is_sample,
        }
        console.log(request_obj)
        form_data.append("req",JSON.stringify(request_obj))
        $.ajax({
        headers: { "X-CSRFToken": token },
        type:"POST",
        url:"http://pnndsrvctvt.com:8000/billing/hul/api/add/",
        data:form_data,
        processData: false,
        contentType: false,
        success:function(response){
            console.log(response)
       		document.getElementById("msgModal").style["display"]="block"
            setTimeout(()=>{document.location.reload(true)},5000)
//        	document.location.reload(true)
//            document.getElementById("stock_records").innerHTML+="<tr style='font-size: 13px;font-weight: 500;word-wrap: break-word;text-align: center;'><td style='border: 1px solid black;'>"+response.id+"</td><td style='border: 1px solid black;'>"+brand+"</td><td style='border: 1px solid black;'>"+variant+"</td><td style='border: 1px solid black;'>"+variant_type+"</td><td style='border: 1px solid black;'>"+packing_type+"</td><td style='border: 1px solid black;'>"+noBoxes+"</td>"+
//            "<td style='border: 1px solid black;'>"+quantity+"</td><td style='border: 1px solid black;'>"+(noBoxes*quantity)+"</td><td style='border: 1px solid black;'>"+receiving_date+"</td><td style='border: 1px solid black;'>"+location_id+"</td><td style='border: 1px solid black;'>"+response.created_at+"</td>"+
//            "<td style='border: 1px solid black;'>"+response.employee_id+"</td><td style='border: 1px solid black;'><a href='localhost:8000/media/"+response.file_path+"' download='localhost:8000/media/"+response.file_path+"'>download</a></td></tr>"
        }
        })
    }else{
        alert("Please fill all details ! ")
    }
}



function get_acitivity_details(evt, activity_id){
request_obj = {
"id" : activity_id
}
var token=document.getElementById("tk").getAttribute("data-token")
$.ajax({

        headers: { "X-CSRFToken": token },
        type:"GET",
        url:"http://pnndsrvctvt.com:8000/billing/hul/api/activity_details/",
        data:request_obj,
        data_type:"json",
        contentType: "application/json",
        success:function(response){
            console.log(response)
            document.getElementById("activity_details_name").innerHTML = response["acitivity_name"]
            document.getElementById("activity_details_order_quantity").innerHTML = response["activity_order"]
            document.getElementById("activity_details_order_buffer_percent").innerHTML = response["activity_buffer_percent"]
            document.getElementById("activity_details_total_order_with_buffer").innerHTML = response["total_quantity_order_with_buffer_percent"]
 //           document.getElementById("activity_details_total_received_order_quanity").innerHTML = response["total_received_quantity"]

            var total_quantity_order_with_buffer_percent = response["total_quantity_order_with_buffer_percent"]
            var total_received_quantity = response["total_received_quantity"]
            var shortfall_quantity = parseInt(total_quantity_order_with_buffer_percent) - parseInt(total_received_quantity)
//            document.getElementById("activity_details_shortfall_received_quanity").innerHTML = shortfall_quantity
//            document.getElementById("activity_details_shortfall_received_quanity").style["color"] = "red"

            for(var i=0;i<response["stock_data"].length;i++){

                document.getElementById("activity_details_records").innerHTML+="<tr style='text-align: center;font-size:12px;word-wrap: break-word;'>"+
                    "<td style='border: 1px solid black;'>"+response["stock_data"][i]["client_name"]+"</td>"+
                    "<td style='border: 1px solid black;'>"+response["stock_data"][i]["location"]+"</td>"+
                    "<td style='border: 1px solid black;'>"+response["stock_data"][i]["receipt_no"]+"</td>"+
                    "<td style='border: 1px solid black;'>"+response["stock_data"][i]["variant"]+"</td>"+
                    "<td style='border: 1px solid black;'>"+response["stock_data"][i]["type_of_material"]+"</td>"+
                    "<td style='border: 1px solid black;'>"+response["stock_data"][i]["total_received_quantity"]+"</td>"+
                    "<td style='border: 1px solid black;'>"+response["stock_data"][i]["receiver"]+"</td>"+
                    "<td style='border: 1px solid black;'>"+
                        "<a href='http://pnndsrvctvt.com:8000/media/"+response["stock_data"][i]["bill"]+"' download='http://pnndsrvctvt.com:8000/media/"+response["stock_data"][i]["bill"]+"'>download</a>"+
                    "</td>"+
//                    "<td>"+response["stock_data"][i]["client_name"]+"</td>"+
//                    "<td>"+response["stock_data"][i]["client_name"]+"</td>"+
//                    "<td>"+response["stock_data"][i]["client_name"]+"</td>"+
//                    "<td>"+response["stock_data"][i]["client_name"]+"</td>"+
//                    "<td>"+response["stock_data"][i]["client_name"]+"</td>"+


                "</tr>"

            }

	for(var i=0;i<response["variant_quantity_balance"].length;i++){
                table_id = 'variant_material_detail_list_'+i
                document.getElementById("detail_variant_material_count").innerHTML+="<p style='color:#4267B2;'>"+response["variant_quantity_balance"][i]["variant_name"]+"</p>"+
                "<table id="+table_id+" style='font-size: 12px;margin-bottom:4px;'>"+
                    "<tr>"+
                        "<td style='border: 1px solid black;'>type of material name</td>"+
                        "<td style='border: 1px solid black;'>total received material</td>"+
                        "<td style='border: 1px solid black;'>material shortfall</td>"+
			"<td style='border: 1px solid black;'>surplus</td>"+
                      "</tr>"+
                "</table>"+
                "<hr style='height:10px;'>";
                for(var j=0;j<response["variant_quantity_balance"][i]["activity_type_of_material_list"].length;j++){
                    document.getElementById(table_id).innerHTML+="<tr>"+

                        "<td style='border: 1px solid black;'>"+response["variant_quantity_balance"][i]["activity_type_of_material_list"][j]["type_of_material_name"]+"</td>"+
                        "<td style='border: 1px solid black;'>"+response["variant_quantity_balance"][i]["activity_type_of_material_list"][j]["total_received_material"]+"</td>"+
                        "<td style='border: 1px solid black;color: red;'>"+response["variant_quantity_balance"][i]["activity_type_of_material_list"][j]["total_received_shortfall_material"]+"</td>"+
             		"<td style='border: 1px solid black;color: green;'>"+response["variant_quantity_balance"][i]["activity_type_of_material_list"][j]["surplus"]+"</td>"+
		       "</tr>"

                }
            }



            document.getElementById("acitivity_details").style["display"]="block"
        }

})

}






function handlemodeldisplay(evt){
if(document.getElementById('activity_details_records')!=null){	
    document.getElementById('activity_details_records').innerHTML='';
}
    document.getElementById('detail_variant_material_count').innerHTML='';
    document.getElementById('acitivity_details').style.display='none';
}




function add_consumption_record_elems(id){
    $('#'+id).append("<div class='consume_records'>"+

                        "<div>"+
                                "<label for='Consumption From Date' style='font-size:20px;font-weight:600px;'>Consumption From Date</label>"+
                                "<input type='date' class='consume_from_date' />"+
                        "</div>"+

                        "<div>"+
                                "<label for='Consumption To Date' style='font-size:20px;font-weight:600px;'>Consumption To Date</label>"+
                                "<input type='date' class='consume_to_date' />"+
                        "</div>"+

                        "<div>"+
                                "<label for='Consumed Quantity' style='font-size:20px;font-weight:600px;'>Consumed Quantity</label>"+
                                "<input type='number' class='consume_quantity' />"+
                        "</div>"+
                     "</div>"+
                     "<hr>"+

    "")

}


function extract_consumption_quantities(){
    consumption_elements = document.getElementsByClassName("consume_records")
    consumption_records_list = []
    for(var i=0;i<consumption_elements.length;i++){
	if(consumption_elements[i].getElementsByClassName("consume_from_date")[0].value!="" &&
        consumption_elements[i].getElementsByClassName("consume_to_date")[0].value!="" &&
        consumption_elements[i].getElementsByClassName("consume_quantity")[0].value!=""){
        	consume_record = {
	            "consume_from_date": consumption_elements[i].getElementsByClassName("consume_from_date")[0].value,
        	    "consume_to_date": consumption_elements[i].getElementsByClassName("consume_to_date")[0].value,
	            "consume_quantity": consumption_elements[i].getElementsByClassName("consume_quantity")[0].value,
       		 }
        	consumption_records_list.push(consume_record)
	}
    }
    return consumption_records_list
}

function hul_consumption_insert(){
    activity_id = document.getElementById("selected_consume_activity").value.split("&-&")[0]
    activity_variant = document.getElementById("selected_variant").value
    activity_location = document.getElementById("selected_location").value
    consumption_records = extract_consumption_quantities();
    console.log(consumption_records)
    var token=document.getElementById("tk").getAttribute("data-token")

        $.ajax({
            headers: { "X-CSRFToken": token },
            type:"POST",
            url:"http://pnndsrvctvt.com:8000/billing/hul/api/consume/quantity",
            data:JSON.stringify({
                "activity_id":activity_id,
                "variant":activity_variant,
                "location":activity_location,
                "consume_records":consumption_records
            }),
            data_type:"json",
            success:function(response){
                console.log(response)
                document.getElementById("msgModal").style["display"]="block"
                setTimeout(()=>{document.location.reload(true)},5000)
            },
            error:function(err){
                console.log(err)
            }
        })
}


function getActivityLocationBrand(evt){
    console.log("getActivityLocationBrand !")
    count = 1
    while(count<document.getElementById("selected_location").childNodes.length){
        document.getElementById("selected_location").removeChild(document.getElementById("selected_location").lastChild);
        count++;
    }
    count = 1
    while(count<document.getElementById("selected_variant").childNodes.length){
        document.getElementById("selected_variant").removeChild(document.getElementById("selected_variant").lastChild);
        count++;
    }

    console.log(document.getElementsByClassName("consume_records").length)
    count = document.getElementsByClassName("consume_records").length - 1
    for(var i=count; i>0; i--){
         document.getElementById("consumption_div").removeChild(document.getElementsByClassName("consume_records")[i])
    }
    document.getElementsByClassName("consume_from_date")[0].value=""
    document.getElementsByClassName("consume_to_date")[0].value=""
    document.getElementsByClassName("consume_quantity")[0].value=""

    var activity_id = document.getElementById("selected_consume_activity").value.split("&-&")[0]
    var token=document.getElementById("tk").getAttribute("data-token")

    $.ajax({
        headers: { "X-CSRFToken": token },
        type:"GET",
        url:"http://pnndsrvctvt.com:8000/billing/hul/api/activity_brand_location_list",
        data:{
                "activity_id": activity_id
            },
        data_type:"json",
        contentType: "application/json",
        success:function(response){

            if(response.status==200){
                console.log(response)
                if(response["activity_variant_list"].length!=0 && response["activity_location_list"].length!=0){
                    for(var i=0;i<response["activity_variant_list"].length;i++){
                        console.log(response["activity_variant_list"][i])
                        newOption = document.createElement('option');
                        newOption.value=response["activity_variant_list"][i];
                        newOption.text=response["activity_variant_list"][i];
                        document.getElementById("selected_variant").appendChild(newOption);

                    }

                    for(var i=0;i<response["activity_location_list"].length;i++){
                        console.log(response["activity_location_list"][i])
                        newOption = document.createElement('option');
                        newOption.value=response["activity_location_list"][i];
                        newOption.text=response["activity_location_list"][i];
                        document.getElementById("selected_location").appendChild(newOption);

                    }
                   document.getElementById("selected_variant").disabled = false
                   document.getElementById("selected_location").disabled = false
                }
                else{
                    alert("No stock present for selected activity! ")
                    document.getElementById("selected_variant").disabled = true
                   document.getElementById("selected_location").disabled = true
                }
            }
        }
    })
}




function get_acitivity_consumption_details(evt, activity_id, variant, location){
    request_obj = {
        "id" : activity_id,
        "variant": variant,
        "location": location
    }
    var token=document.getElementById("tk").getAttribute("data-token")
    $.ajax({

            headers: { "X-CSRFToken": token },
            type:"GET",
            url:"http://pnndsrvctvt.com:8000/billing/hul/api/activity_consumption_details/",
            data:request_obj,
            data_type:"json",
            contentType: "application/json",
            success:function(response){
                console.log(response)
                document.getElementById("activity_details_name").innerHTML = response["acitivity_name"]
                document.getElementById("activity_details_order_quantity").innerHTML = response["activity_order"]
                document.getElementById("activity_details_order_buffer_percent").innerHTML = response["activity_buffer_percent"]
                document.getElementById("activity_details_total_order_with_buffer").innerHTML = response["total_quantity_order_with_buffer_percent"]


                var total_quantity_order_with_buffer_percent = response["total_quantity_order_with_buffer_percent"]
                var total_received_quantity = response["total_received_quantity"]
                var shortfall_quantity = parseInt(total_quantity_order_with_buffer_percent) - parseInt(total_received_quantity)


//                for(var i=0;i<response["stock_data"].length;i++){
//
//                    document.getElementById("activity_details_records").innerHTML+="<tr style='text-align: center;font-size:12px;word-wrap: break-word;'>"+
//                        "<td style='border: 1px solid black;'>"+response["stock_data"][i]["client_name"]+"</td>"+
//                        "<td style='border: 1px solid black;'>"+response["stock_data"][i]["location"]+"</td>"+
//                        "<td style='border: 1px solid black;'>"+response["stock_data"][i]["receipt_no"]+"</td>"+
//                        "<td style='border: 1px solid black;'>"+response["stock_data"][i]["variant"]+"</td>"+
//                        "<td style='border: 1px solid black;'>"+response["stock_data"][i]["type_of_material"]+"</td>"+
//                        "<td style='border: 1px solid black;'>"+response["stock_data"][i]["total_received_quantity"]+"</td>"+
//                        "<td style='border: 1px solid black;'>"+response["stock_data"][i]["receiver"]+"</td>"+
//                    "</tr>"
//                }


                for(var i=0;i<response["variant_quantity_balance"].length;i++){
                    table_id = 'variant_material_detail_list_'+i
                    document.getElementById("detail_variant_material_count").innerHTML+="<p style='color:#4267B2;'>"+response["variant_quantity_balance"][i]["variant_name"]+"</p>"+
                    "<table id="+table_id+" style='font-size: 12px;margin-bottom:4px;'>"+
                        "<tr>"+
                            "<td style='border: 1px solid black;'>type of material name</td>"+
                            "<td style='border: 1px solid black;'>total received material</td>"+
                            "<td style='border: 1px solid black;'>material shortfall</td>"+
                            "<td style='border: 1px solid black;'>consumed quantity</td>"+
                            "<td style='border: 1px solid black;'>Balance Received quantity</td>"+
                          "</tr>"+
                    "</table>"+
                    "<hr style='height:10px;'>";
                    for(var j=0;j<response["variant_quantity_balance"][i]["activity_type_of_material_list"].length;j++){
                        document.getElementById(table_id).innerHTML+="<tr>"+

                            "<td style='border: 1px solid black;'>"+response["variant_quantity_balance"][i]["activity_type_of_material_list"][j]["type_of_material_name"]+"</td>"+
                            "<td style='border: 1px solid black;'>"+response["variant_quantity_balance"][i]["activity_type_of_material_list"][j]["total_received_material"]+"</td>"+
                            "<td style='border: 1px solid black;color: red;'>"+response["variant_quantity_balance"][i]["activity_type_of_material_list"][j]["total_received_shortfall_material"]+"</td>"+
                            "<td style='border: 1px solid black;color: red;'>"+load_quantity(response["variant_quantity_balance"][i]["activity_type_of_material_list"][j]["consumed_quantity"])+"</td>"+
                            "<td style='border: 1px solid black;color: red;'>"+balance_quantity(response["variant_quantity_balance"][i]["activity_type_of_material_list"][j]["total_received_material"],response["variant_quantity_balance"][i]["activity_type_of_material_list"][j]["consumed_quantity"])+"</td>"+
                        "</tr>"

                    }
                }

                document.getElementById("acitivity_details").style["display"]="block"
                document.getElementById("view_consumption").setAttribute('onclick',"get_activity_consumption_records(this,'"+activity_id+"')")
            }

    })


}




function load_quantity(quantity){
    console.log(quantity," quantity")
    if(quantity=="undefined" || quantity==undefined){
        return 0
    }
    return quantity
}

function balance_quantity(received_quantity, consumed_quantity){
    if(consumed_quantity=="undefined" || consumed_quantity==undefined){
        return received_quantity
    }
    return parseInt(received_quantity) - parseInt(consumed_quantity)
}


function get_activity_consumption_records(evt, id){
    console.log("id::", id)
  request_obj = {
        "id" : id,
    }
    var token=document.getElementById("tk").getAttribute("data-token")
    $.ajax({

            headers: { "X-CSRFToken": token },
            type:"GET",
            url:"http://pnndsrvctvt.com:8000/billing/hul/api/activity_consumption_records",
            data:request_obj,
            data_type:"json",
            contentType: "application/json",
            success:function(response){
                console.log(response)
                document.getElementById("display_records_quantity").innerHTML = "<tr><td style='border: 1px solid black;'>Consumption Quantity</td>"+
                "<td style='border: 1px solid black;'>From Date</td>"+
                "<td style='border: 1px solid black;'>To date</td>"+
                "</tr>"
                for(var i=0;i<response["records_list"].length;i++){
                    for(var j=0;j<response["records_list"][i].length;j++){
                        document.getElementById("display_records_quantity").innerHTML+="<tr>"+
                            "<td style='border: 1px solid black;'>"+response["records_list"][i][j]["consumption_quantity"]+"</td>" +
                            "<td style='border: 1px solid black;'>"+response["records_list"][i][j]["from_date"]+"</td>" +
                            "<td style='border: 1px solid black;'>"+response["records_list"][i][j]["to_date"]+"</td>" +
                        "</tr>"
                    }
                }

                document.getElementById("display_records").style["display"]="block"

            }

    })

}


function handel_close_evt(evt){
    document.getElementById("display_records").style["display"]="none";
}
//HUL ENDS

