

function getProjectId(projId,projName,projActive){
    console.log('getProjectId:::',projId,projName,projActive)
    }
function getsugg(){
    console.log(document.getElementById('search_text').value)
    document.getElementById("search_form").submit();
}

function proj_analysis(){
    console.log("analysis:::",document.getElementById("selected_proj").value);
    proj_id = document.getElementById("selected_proj").value.split("$-$")[0];
    proj_name = document.getElementById("selected_proj").value.split("$-$")[1];
    document.getElementById("proj_id").value=proj_id;
    document.getElementById("proj_name").value=proj_name;
    document.getElementById("proj_analysis").submit();
}



class Analysis{
    constructor(){
        console.log("constructor ");
//        document.getElementById("search_div").style["display"]="none";
    }

}

analysis = new Analysis();