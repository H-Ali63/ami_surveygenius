var location_array = []
var state_array = []



function formatDate(date) {
    var d = new Date(date),
        month = '' + (d.getMonth() + 1),
        day =  d.getDate(),
        year = d.getFullYear();
//alert(d.getDate()+'---'+day);
    if (month.length < 2)
        month = '0' + month;
    return [year, month, day].join('-');
}

Array.min = function( array ){
    return Math.min.apply( Math, array );
};

function titleCase(str) {
                      return str.split(' ').map(function(val){
                        return val.charAt(0).toUpperCase() + val.substr(1).toLowerCase();
                      }).join(' ');
                    }

function select_activity_variant(evt){

    var urls = document.getElementById("myurl").value;
    console.log(urls,'urls_select_activity_variant')
   // alert(evt.value.trim());

    console.log("evt", evt.value)
//    count = 1
//    while(count<document.getElementById("selected_location").childNodes.length){
//        document.getElementById("selected_location").removeChild(document.getElementById("selected_location").lastChild);
//        count++;
//    }
//    count = 1
  //  while(count<document.getElementById("selected_variant").childNodes.length){
    //    document.getElementById("selected_variant").removeChild(document.getElementById("selected_variant").lastChild);
      //  count++;
    //}
    activity_name = document.getElementById("activity").value
    var variant = evt.value.trim()
    var token=document.getElementById("tk").getAttribute("data-token")

    var checkurl = "http://103.218.101.38:8000/billing/"+urls+"/api/activity_report_location_list"

    console.log(checkurl,'checkurl')

    if(activity_name!="default"){
        $.ajax({
        headers: { "X-CSRFToken": token },
        type:"GET",

        url:checkurl,

        data:{
                "activity_name": activity_name,
                "variant":variant
            },
        data_type:"json",
        contentType: "application/json",
        success:function(response){
            if(response.status==200){
                console.log(response,'====================================vijay')
                //alert(response["act_start_date"].created_date);
                document.getElementById("act_start_date").value =response["act_start_date"].created_date
                if(response["activity_variant_list"].length!=0 ){
                    document.getElementById("location_list_values").innerHTML = ""
                    document.getElementById("state_list_values").innerHTML = ""

                    for(var i=0;i<response["activity_location_list"].length;i++){
                        console.log(response["activity_location_list"][i])
                        divnewOption = document.createElement('div');
                        divnewOption.setAttribute("style","border: 1px solid black; width: 20%; margin-left: 6%;")
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
                    for(var i=0;i<response["activity_state_list"].length;i++){
                        console.log(response["activity_state_list"][i])
                        divnewOption = document.createElement('div');
                        divnewOption.setAttribute("style","border: 1px solid black; width: 20%; margin-left: 6%;")
                        newOption = document.createElement('input');
                        newOption.type = "checkbox"
                        newOption.value=response["activity_state_list"][i];
                        newOption.setAttribute("onclick", "select_state_values(this)")
                        spannewOption = document.createElement('span');
                        spannewOption.textContent = response["activity_state_list"][i]

                        divnewOption.appendChild(newOption)
                        divnewOption.appendChild(spannewOption)

                        document.getElementById("state_list_values").appendChild(divnewOption);
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
    document.getElementById("state_list_values").innerHTML = ""

    location_array = []
    state_array=[]
    }


}

function select_activity_report(evt){
    console.log("evt_select_activity_report", evt.value)
    state_array=[]
    location_array = []

    var urls =document.getElementById("myurl").value;
    console.log(urls,'=============urls_select_activity_report')


    count = 1
    while(count<document.getElementById("selected_variant").childNodes.length){
        document.getElementById("selected_variant").removeChild(document.getElementById("selected_variant").lastChild);
        count++;
    }
    var variant='variant';
    var activity_name = evt.value.trim()
    console.log(activity_name,'=======activity_namesss')


    var checkurl = "http://103.218.101.38:8000/billing/"+urls+"/api/activity_report_location_list"

    console.log(checkurl,'checkurlssssssssssssss')



    var token=document.getElementById("tk").getAttribute("data-token")

    console.log('tokensssssssss')


    if(activity_name!="default"){
        $.ajax({
        headers: { "X-CSRFToken": token },

        type:"GET",
        url:checkurl,
        data:{
                "activity_name": activity_name,
                 "variant":'variant'
            },
        data_type:"json",
        contentType: "application/json",
        success:function(response){
            if(response.status==200){
                console.log(response,'======response_select_activity_report')
                //alert(response["act_start_date"].created_date);
                document.getElementById("selected_variant").disabled = false

                document.getElementById("act_start_date").value =response["act_start_date"].created_date
                 if(response["activity_variant_list"].length!=0 ){

                    for(var i=0;i<response["activity_variant_list"].length;i++){
                        console.log(response["activity_variant_list"][i])
                        newOption = document.createElement('option');
                        newOption.value=response["activity_variant_list"][i];
                        newOption.text=response["activity_variant_list"][i];
                        document.getElementById("selected_variant").appendChild(newOption);

                    }
                    }
                    else
                    {
                     alert("No stock present for selected activity! ")
                     document.getElementById("selected_variant").disabled = true
                    }
}
}


    })
    }



}


    
  

function activity_report_file(){

    var urls = document.getElementById("myurl").value;
    console.log(urls,'urls__activity_report_file')


    document.getElementById("detail_report").innerHTML = "";
    document.getElementById("detail_report_details").innerHTML = "";
    document.getElementById("location_array_list").value ="";
    var nowDate = new Date();
    var day = nowDate.getDate();
    var month = nowDate.getMonth()+1;
    if (month.length < 2)
            month = '0' + month;
    if (day.length < 2)
        day = '0' + day;
    var to_date = nowDate.getFullYear()+'-'+(month)+'-'+day;
    //to_date =formatDate(to_date);
    activity_name = document.getElementById("activity").value
    variant = document.getElementById("selected_variant").value
//    location = document.getElementById("location").value
    from_date = formatDate(document.getElementById("act_start_date").value)
    // alert('from date --'+document.getElementById("act_start_date").value);

    to_date = to_date
    console.log("activity_name::=======", activity_name," variant::============",variant, "from_date:::",from_date, "to_date:::",to_date)
    var token=document.getElementById("tk").getAttribute("data-token")
    console.log(from_date,"======",to_date)
    if(activity_name!="default"){
        document.getElementById("location_array_list").value=''
        document.getElementById("location_array_list").value = location_array.join()
        document.getElementById("state_array_list").value = state_array.join()

         var checkurl = "http://103.218.101.38:8000/billing/"+urls+"/api/my_reports"

        console.log(checkurl,'==============checkurl/api/my_reports/')





        $.ajax({
        headers: { "X-CSRFToken": token },
        type:"GET",
        url:checkurl,

        data:{
                "activity_name": activity_name,
                "variant": variant,
                "from_date": from_date,
                "to_date": to_date,
                "location": location_array.join(),
                "location_state": state_array.join()

            },
        data_type:"json",
        contentType: "application/json",
        
        success:function(response){
            if(response.status==200){
                console.log("-------testing-------"+response);
                console.log("=========================================================")
                    var state_location,report_location,st_date,end_date,month_val='';
                    report_location='';
                    state_location='';
                    
                    //alert(document.getElementById("state_array_list").value);
                    const monthNames = ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"];
                    for(var i=0;i<response["activity_stock_consume_data"].new_stock_list_data.length;i++){
                      report_location += titleCase(response.activity_stock_consume_data.new_stock_list_data[i].location)+" , " ;
                     }
                     report_location=report_location.substring(0, report_location.length - 2);
                     var nowDate = new Date();
                     st_date = document.getElementById("act_start_date").value;// new Date(document.getElementById("from_date").value);
                     end_date =nowDate;//new Date(document.getElementById("to_date").value);

                     //alert(report_location);
                     var test_1,test_2,test_3,test_4,test_5,test_6,test_7,test_8,test_9,test_10='';
                    document.getElementById("detail_report").innerHTML+= "<table style='font-size: 16px;border:1px solid black'>"+ "<tr style='font-size: 16px;border:1px solid black'><td style='font-size: 16px;background-color: LightBlue;border:1px solid black'><b>Brand:</b></td><td style='font-size: 16px;border:1px solid black'>"+response.variant+"</td></tr>"+
                    "<tr style='font-size: 16px;border:1px solid black'><td style='font-size: 16px;background-color: LightBlue;border:1px solid black'><b>Activity Name:</b></td><td>"+response.activity_stock_consume_data.activity_name+"</td></tr>"+
                    "<tr ><td style='font-size: 16px;background-color: LightBlue;border:1px solid black'><b>State:</b></td><td style='font-size: 16px;border:1px solid black'>"+ document.getElementById("state_array_list").value +"</td></tr><tr ><td style='font-size: 16px;background-color: LightBlue;border:1px solid black'><b>City:</b></td><td style='font-size: 16px;border:1px solid black'>"+ report_location +"</td></tr><!--<tr><td style='font-size: 16px;background-color: LightBlue;border:1px solid black'><b>Activity Start Date:</td><td style='font-size: 16px;border:1px solid black'>"+response.start_date +"</td></tr>--></table><BR>";



                    document.getElementById("detail_report_details").innerHTML+="<table   id='test' style='font-size: 16px;border:1px solid black'>";
                    test_1 ="<tr  style='font-size: 16px;background-color: LightBlue;border:1px solid black'><td style='font-size: 16px;border:1px solid black'><b>City</b></td>";
                    for(var i=0;i<response["activity_stock_consume_data"].new_stock_list_data.length;i++)
                    {
                      test_1+="<td style='font-size: 16px;border:1px solid black'><b>"+titleCase(response.activity_stock_consume_data.new_stock_list_data[i].location)+"</td>";
                    }
                      test_1+="<td style='font-size: 16px;border:1px solid black'><b>Total</b></td>";

                    document.getElementById("test").innerHTML+=test_1;
                    document.getElementById("test").innerHTML+="</tr>";
                     test_2="<tr style='font-size: 16px;border:1px solid black'><td style='font-size: 16px;background-color: LightBlue;border:1px solid black'><b>Consumption Start Date</b></td>";

                     for(var i=0;i<response["activity_stock_consume_data"].new_stock_list_data.length;i++)
                    {
                    if(response.activity_stock_consume_data.consumption_start_date != null)
                    {
                            test_2+="<td  style='font-size: 16px;border:1px solid black'>"+ response.activity_stock_consume_data.consumption_start_date+"</td>";
                            //test_2+="<td  style='font-size: 16px;border:1px solid black'></td>";


                   }
                   else
                   {
                       test_2+="<td  style='font-size: 16px;border:1px solid black'>-</td>";

                   }
                   }
                     test_2+="<td style='font-size: 16px;'></td>";

                    document.getElementById("test").innerHTML+=test_2;

                    document.getElementById("test").innerHTML+="</tr>";
                    var total_quantity='';
                    test_3="<tr style='font-size: 16px;border:1px solid black'><td style='font-size: 16px;background-color: LightBlue;border:1px solid black'><b>Total Order Quantity</b></td>";
                     var tot_samples =0;
                     var sample_total=0;


                  for(var r=0;r<response["activity_stock_consume_data"].new_stock_list_data.length;r++)
                   {
                    for(var i=0;i<response["activity_stock_consume_data"].activity_total_order_quantity.length;i++)
                    {
                            if(titleCase(response["activity_stock_consume_data"].activity_total_order_quantity[i].location)==titleCase(response["activity_stock_consume_data"].new_stock_list_data[r].location))
                            {
                            test_3+="<td  style='font-size: 16px;border:1px solid black'>"+response.activity_stock_consume_data.activity_total_order_quantity[i].dcount+"</td>";
                            total_quantity = Number(total_quantity)+Number(response.activity_stock_consume_data.activity_total_order_quantity[i].dcount);
                            }
                    }
                    }
                    test_3+="<td style='font-size: 16px;border:1px solid black'>"+total_quantity+"</td>";

                    document.getElementById("test").innerHTML+=test_3;

                    document.getElementById("test").innerHTML+="</tr>";
  
 //--------

                    total_quantity =0;
                    var sample_quantity_array = [];
                    sample_q=0;

                    test_4="<tr style='font-size: 16px;border:1px solid black'><td style='font-size: 16px;background-color: LightBlue;border:1px solid black'><b>Samples Received</b></td>";
                    for(var i=0;i<response["activity_stock_consume_data"].new_stock_list_data.length;i++)
                    {
                            //alert(response["activity_stock_consume_data"].stock_list_data[i].stocks.length);
                            if(response["activity_stock_consume_data"].stock_list_data[i].stocks.length>0)
                            {
                                 for(var bb=0;bb<response["activity_stock_consume_data"].stock_list_data[i].stocks.length;bb++)
                                {
                                    sample_quantity_array[bb] = response["activity_stock_consume_data"].stock_list_data[i].stocks[bb].total_type_of_materials;
                                }
                            }
                            sample_q = Array.min(sample_quantity_array);
                            //alert(sample_q);
                            test_4+="<td  style='font-size: 16px;border:1px solid black'>"+ sample_q +"</td>";
                            total_quantity = Number(total_quantity)+Number(sample_q);
                    }
                    test_4+="<td style='font-size: 16px;border:1px solid black'>"+total_quantity+"</td>";
                    document.getElementById("test").innerHTML+=test_4;
                    document.getElementById("test").innerHTML+="</tr>";

        
                     for(var i=0;i<response["activity_stock_consume_data"].stock_list_data.length;i++)
                    {
                       var kit_received = 'kits_received' in response.activity_stock_consume_data.stock_list_data[i] || '';

                    }
                    if (kit_received=='')
                    {}
                    else
                    {
                        test_5="<tr style='font-size: 16px;border:1px solid black'><td style='font-size: 16px;background-color: LightBlue;border:1px solid black'><b>KIT Received</b></td>";
                        for(var i=0;i<response["activity_stock_consume_data"].stock_list_data.length;i++)
                        {

                                //test_5+="<td  style='font-size: 16px;border:1px solid black'>"+response.activity_stock_consume_data.stock_list_data[i].order_quantity+"</td>";
                                test_5+="<td  style='font-size: 16px;background-color: LightBlue;border:1px solid black'></td>";
                        }
                        test_5+="<td style='font-size: 16px;border:1px solid black'></td>";

                        document.getElementById("test").innerHTML+=test_5;
                        document.getElementById("test").innerHTML+="</tr>";
                    }
                    //-----
                       //--------

                        test_6="<tr style='font-size: 16px;border:1px solid black'><td style='font-size: 16px;background-color: LightBlue;border:1px solid black'><b>Samples Surplus / Shortfall</b></td>";
                        var tot_samples =0;
                        var sample_short=0;
                         var total_sample_short=0;
                   
                        for(var i=0;i<response["activity_stock_consume_data"].new_stock_list_data.length;i++)
                                {
                                                            if(response["activity_stock_consume_data"].stock_list_data[i].stocks.length>0)
                            {
                                 for(var bb=0;bb<response["activity_stock_consume_data"].stock_list_data[i].stocks.length;bb++)
                                {
                                    sample_quantity_array[bb] = response["activity_stock_consume_data"].stock_list_data[i].stocks[bb].total_type_of_materials;
                                }
                            }
                            sample_q = Array.min(sample_quantity_array);
                                   total_quantity = Number(response.activity_stock_consume_data.activity_total_order_quantity[i].dcount);
                                   //tot_samples = Number(response.activity_stock_consume_data.new_stock_list_data[i].total_received_quantity);
                                   tot_samples = sample_q

                                sample_short = Number(total_quantity)-Number(tot_samples);
                                                      
                                total_sample_short +=sample_short;

                             if(sample_short>0)
                         {
                             sample_short = Number(sample_short) *-1;
                             test_6+="<td  style='font-size: 16px;background-color: #F08080;border:1px solid black'>"+sample_short+"</td>";
                         }else{
                                sample_short = Number(sample_short) *-1;
                                test_6+="<td  style='font-size: 16px;background-color: #90EE90;border:1px solid black'>"+sample_short+"</td>";

                         }

                        }
                         if(total_sample_short>0)
                         {
                             total_sample_short = Number(total_sample_short) *-1;
                             test_6+="<td  style='font-size: 16px;background-color: #F08080;border:1px solid black'>"+total_sample_short+"</td>";
                         }else{
                                total_sample_short = Number(total_sample_short) *-1;
                                test_6+="<td  style='font-size: 16px;background-color: #90EE90;border:1px solid black'>"+total_sample_short+"</td>";

                         }
                        document.getElementById("test").innerHTML+=test_6;
                        document.getElementById("test").innerHTML+="</tr>";

                  
                            test_8='';
                             var tr_test8 = '';
                             var  null_replacement='';
                             var  tot_weekly=0;
                             var firstVar1;
                             tr_test8+="<tr style='font-size: 16px;border:1px solid black'>";
                     if(response.activity_stock_consume_data.stock_list_data[0] != null)
                        console.log(response.activity_stock_consume_data,'=================stock_list_data')

                    {
                             for(var k=0;k<response["activity_stock_consume_data"].stock_list_data[0].week_consumption.length-1;k++)
                                    {

                                       // test_8+="<td style='font-size: 16px;background-color: LightBlue;border:1px solid black'><b>Consumption  for  " +response.activity_stock_consume_data.stock_list_data[0].week_consumption[k].from_date+" to " +response.activity_stock_consume_data.stock_list_data[0].week_consumption[k].to_date+ "</b></td>";
                                    }
                             
                             for(var k=0;k<response["activity_stock_consume_data"].new_stock_list_data[0].week_consumption.length;k++)
                                    {
                                        tot_weekly =0;
                                        var p=0;
                                        //alert(k);
                                        p=k+1;
                                        //test_8+="<td style='font-size: 16px;background-color: LightBlue;border:1px solid black'><b>Consumption  for  " +response.activity_stock_consume_data.stock_list_data[0].week_consumption[k].from_date+" to " +response.activity_stock_consume_data.stock_list_data[0].week_consumption[k].to_date+ "</b></td>";
                                        test_8+="<td style='font-size: 16px;background-color: LightBlue;border:1px solid black'><b>Consumption  for Week "+p+"</b></td>";
                                        num_location = response["activity_stock_consume_data"].new_stock_list_data.length;
                                        for (p=0;p<num_location;p++)
                                        {
                                        firstVar1 = (response.activity_stock_consume_data.new_stock_list_data[p].week_consumption[k].consumption != null) ? response.activity_stock_consume_data.new_stock_list_data[p].week_consumption[k].consumption :"0";
                                        tot_weekly +=Number(firstVar1);
                                        test_8+="<td style='font-size: 16px;border:1px solid black'>"+ firstVar1 +"</td>";
                                        }
                                        test_8+="<td  style='font-size: 16px;border:1px solid black'>"+tot_weekly+"</td></tr>";

                                        test_8 +="</tr>"
                                    }
                                    document.getElementById("test").innerHTML+=tr_test8;
                                    document.getElementById("test").innerHTML+=test_8;
                                
                    }
                                

                                                
                            
                            // for(var i=0;i<response["activity_stock_consume_data"].stock_list_data.length;i++)
                            // {
                            //     tr_test8='';
                            //      p=1;
                            //       total_weekly_consumptionvar1='';
                            //  alert('for loop + '+response["activity_stock_consume_data"].stock_list_data[i].week_consumption.length);

                            //  for(var k=0;k<response["activity_stock_consume_data"].stock_list_data[i].week_consumption.length;k++)
                            //         {
                                        
                            //             test_8+="<td style='font-size: 16px;border:1px solid black'><b>"+response.activity_stock_consume_data.stock_list_data[i].week_consumption[k].consumption+ "</b></td>";

                                        
                            //         }
                            //         document.getElementById("test").innerHTML+=tr_test8;
                            //         document.getElementById("test").innerHTML+=test_8;
                            //         test_8 +="</tr>"


                            // }

                            //-----
                                                              //--------

                                         //--------
//------------------------------------------------------------------------------------------------------

                        }

                           
                       for(var i=0;i<response["activity_stock_consume_data"].stock_list_data.length;i++)
                       {
                        var week_con = 'week_consumption' in response.activity_stock_consume_data.new_stock_list_data[i] || '';
                        // alert(" Week Consumption - "+week_con);

                        if(week_con!='')
                        {
                            console.log(response["activity_stock_consume_data"],'==================')
                                         var  total_weekly_consumption_hor=0;
                                                            test_10="<tr style='font-size: 16px;backgroundColor:red;border:1px solid black'><td style='font-size: 16px;background-color: LightBlue;border:1px solid black'><b>Total samples distributed</b></td>";
                                                            total_weekly_consumptionvar1=0;
                                                            total_weekly_consumption_hor=0;

                                                            for(var i=0;i<response["activity_stock_consume_data"].new_stock_list_data.length;i++)
                                                            {
                                                            total_weekly_consumptionvar1=0;
                                                                    for(var k=0;k<response["activity_stock_consume_data"].new_stock_list_data[i].week_consumption.length;k++)
                                                                    {
                                                                        if (response.activity_stock_consume_data.new_stock_list_data[i].week_consumption[k].consumption!=null)
                                                                        {
                                                                        total_weekly_consumptionvar1 += Number(response.activity_stock_consume_data.new_stock_list_data[i].week_consumption[k].consumption);
                                                                        }

                                                                    }
                                                                    test_10+="<td  style='font-size: 16px;border:1px solid black'>"+total_weekly_consumptionvar1+"</td>";
                                                                        total_weekly_consumption_hor+=Number(total_weekly_consumptionvar1);

                                                            }
                                                            test_10+="<td  style='font-size: 16px;border:1px solid black'>"+total_weekly_consumption_hor+"</td>";

                                                         //   document.getElementById("test").innerHTML+=test_10;
                                                           // document.getElementById("test").innerHTML+="</tr>";
                                                            //-----
                                                             //--------
                                                             total_weekly_consumptionvar1='';

                                 document.getElementById("test").innerHTML+=test_10;
                               document.getElementById("test").innerHTML+="</tr>";
                        }
                       for(var i=0;i<response["activity_stock_consume_data"].stock_list_data.length;i++)
                       {
                        var week_con = 'week_consumption' in response.activity_stock_consume_data.stock_list_data[i] || '';
                        // alert(" Week Consumption 2- "+week_con);

                        if(week_con!='')
                        {

                    test_9="<tr style='font-size: 16px;border:1px solid black'><td style='font-size: 16px;background-color: LightBlue;border:1px solid black'><b>Total Samples to be distributed (as per order)</b></td>";
                    var total_order_quantity='';
                    var total_distribution_quantity='';
                    var total_distribution_quantity_hor=0;
                 for(var i=0;i<response["activity_stock_consume_data"].new_stock_list_data.length;i++)
                    {
                    total_weekly_consumptionvar1='';
                    total_order_quantity = Number(response.activity_stock_consume_data.activity_total_order_quantity[i].dcount);
                            for(var k=0;k<response["activity_stock_consume_data"].new_stock_list_data[i].week_consumption.length;k++)
                            {
                            if (response.activity_stock_consume_data.new_stock_list_data[i].week_consumption[k].consumption!=null)
                            {
                            total_weekly_consumptionvar1  =Number(total_weekly_consumptionvar1) + Number(response.activity_stock_consume_data.new_stock_list_data[i].week_consumption[k].consumption);
                            }
                            }
                            total_distribution_quantity =Number(total_order_quantity)- Number(total_weekly_consumptionvar1);
                            test_9+="<td  style='font-size: 16px;border:1px solid black'>"+total_distribution_quantity+"</td>";
                            total_distribution_quantity_hor +=Number(total_distribution_quantity);
                    }
                    test_9+="<td  style='font-size: 16px;border:1px solid black'>"+total_distribution_quantity_hor+"</td>";

                    document.getElementById("test").innerHTML+=test_9;
                    document.getElementById("test").innerHTML+="</tr>";
                   } //-----
                     else
                            {
                              document.getElementById("test").innerHTML+="<tr style='font-size: 16px;border:1px solid black'><td style='font-size: 16px;background-color: LightBlue;border:1px solid black'></td></tr>";
                            }
                    }
                   document.getElementById("test").innerHTML+="</table>";

            }
        }
    })

}

}



function select_state_values(event){

    if(state_array.indexOf(event.value)==-1){
        state_array.push(event.value)
    }else{
        select_value_index_from_list = state_array.indexOf(event.value)

        state_array.splice(select_value_index_from_list, 1)
    }
    console.log(state_array)
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

function show_state_tags(event){
    if(document.getElementById("state_list_values").style.display == "block"){
        document.getElementById("state_list_values").style.display = "none"
    }else{
        document.getElementById("state_list_values").style.display = "block"
    }
}
function show_location_tags(event){
    if(document.getElementById("location_list_values").style.display == "block"){
        document.getElementById("location_list_values").style.display = "none"
    }else{
        document.getElementById("location_list_values").style.display = "block"
    }
}