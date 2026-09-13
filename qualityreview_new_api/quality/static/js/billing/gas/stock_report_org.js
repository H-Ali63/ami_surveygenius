var location_array = []

function select_activity_report(evt){
    console.log("evt", evt.value)
//    count = 1
//    while(count<document.getElementById("selected_location").childNodes.length){
//        document.getElementById("selected_location").removeChild(document.getElementById("selected_location").lastChild);
//        count++;
//    }
    count = 1
    while(count<document.getElementById("selected_variant").childNodes.length){
        document.getElementById("selected_variant").removeChild(document.getElementById("selected_variant").lastChild);
        count++;
    }

    var activity_name = evt.value.trim()
    console.log(activity_name)
    var token=document.getElementById("tk").getAttribute("data-token")
    if(activity_name!="default"){
        $.ajax({
        headers: { "X-CSRFToken": token },
        type:"GET",
        url:"http://pnndsrvctvt.com:8000/billing/hul/api/activity_report_location_list",
        data:{
                "activity_name": activity_name
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
                        divnewOption = document.createElement('div');
                        newOption = document.createElement('input');
                        newOption.type = "checkbox"
                        newOption.value=response["activity_location_list"][i];
                        newOption.setAttribute("onclick", "select_location_values(this)")
                        spannewOption = document.createElement('span');
                        spannewOption.textContent = response["activity_location_list"][i]

                        divnewOption.appendChild(newOption)
                        divnewOption.appendChild(spannewOption)

                        document.getElementById("location_list_values").appendChild(divnewOption);
//                        document.getElementById("location_list_values").appendChild(divnewOption);

                    }
                   document.getElementById("selected_variant").disabled = false
//                   document.getElementById("selected_location").disabled = false
                }
                else{
                    alert("No stock present for selected activity! ")
                    document.getElementById("selected_variant").disabled = true
//                   document.getElementById("selected_location").disabled = true
                }
            }
        }
    })
    }
    else{
    document.getElementById("selected_variant").disabled = true
    document.getElementById("location_list_values").innerHTML = ""
    location_array = []
    }


}


function activity_report_file(){
    activity_name = document.getElementById("activity").value
    variant = document.getElementById("selected_variant").value
//    location = document.getElementById("location").value
    from_date = document.getElementById("from_date").value
    to_date = document.getElementById("to_date").value
    console.log("activity_name::", activity_name," variant::",variant, "from_date:::",from_date, "to_date:::",to_date)
    var token=document.getElementById("tk").getAttribute("data-token")

    if(activity_name!="default"){

        document.getElementById("location_array_list").value = location_array.join()
	if(from_date<to_date){
            document.getElementById("report_form").submit()
        }else{
            alert("To Date must be greater than From Date !")
        }
        
//        $.ajax({
//        headers: { "X-CSRFToken": token },
//        type:"GET",
//        url:"http://localhost:8000/billing/hul/api/reports/",
//        data:{
//                "activity_name": activity_name,
//                "variant": variant,
//                "from_date": from_date,
//                "to_date": to_date,
//                "location": location_array.join()
//            },
//        data_type:"json",
//        contentType: "application/json",
//        success:function(response){
//
//            if(response.status==200){
//                console.log(response)
//            }
//        }
//    })
    }else{alert(" Please select proper Input")}
}



function select_location_values(event){

    if(location_array.indexOf(event.value)==-1){
        location_array.push(event.value)
    }else{
        select_value_index_from_list = location_array.indexOf(event.value)

        location_array.splice(select_value_index_from_list, 1)
    }
    console.log(location_array)
}


function show_location_tags(event){
    if(document.getElementById("location_list_values").style.display == "block"){
        document.getElementById("location_list_values").style.display = "none"
    }else{
        document.getElementById("location_list_values").style.display = "block"
    }
}
