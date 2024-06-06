document.addEventListener("DOMContentLoaded",function(){
    var select = document.getElementById('select');
    document.querySelector('#select').addEventListener('click', selectFunction)
    document.querySelector('#search_field').addEventListener('input', searchSuggestions)
    document.querySelector('#proccessJsonFile').addEventListener('click', proccesJsonFile)
    document.querySelector('#generateJsonFile').addEventListener('click', generateJsonFile)
    document.querySelector('#reset_db').addEventListener('click', reset_db)
    document.querySelector('#load_new_substances').addEventListener('click', load_new_substances)
    document.querySelector('#delete_search_results').addEventListener('click', delete_search_results)

    select.addEventListener('mouseenter', function() {
      this.size = this.options.length;
    });
    
    select.addEventListener('mouseleave', function() {
      this.size = 1;
    });
  });
var resetInterval; 
function selectFunction(){
let select = document.querySelector('#select');
let value = select.value;
if (value=="molecular_mass"){
    let abweichung = document.querySelector('#abweichung');
    abweichung.style["display"] = "block";
}
if(value != "molecular_mass"){
    let abweichung = document.querySelector('#abweichung');
    abweichung.style["display"] = "none";
}
}

function show_reset_progress(resetInterval){
    $.ajax({
        type: 'GET',
        url: "/webscraper/request_how_many_json_file",
        success: function(response) {
            $(".progressbar").width(response.progress +"%");
            console.log(response.progress)
            if (response.progress >= 95){
                $(".progressbar").width("0%"); 
                clearInterval(resetInterval);
                document.querySelector('.progressbar').style['display'] = "none";
                document.querySelector('.progress_message').style["display"]= "none"; 
                document.querySelector('.show_witz').style["display"]= "none";
                 try{  
                var answer = document.querySelector('.answer');
                 answer.style["display"] = "flex";}
                 catch{
                    
                 }
    
                changeBackground();
                var answer = document.querySelector('.answer');
                if(answer != null){answer.style["display"] = "block";}
                var message = document.querySelector('.show_massebereich');
                if(message != null){message.style["display"] = "flex";}
            }
        },
        error: function(response) {
            $("#.rogressbar").width("0%");
        }
    });
    $.ajax({
        typ:'GET',
        url: "/webscraper/get_witz",
        success:function(response){
            var show_witz = document.querySelector('.show_witz');
            show_witz.style["display"] = "flex";
            show_witz.innerHTML = response.witz;
        },
        error:function(response){alert("error")},
    });
}

function reset_db(){
    alert("starting to reset_db")
    changeBackground();
    var answer = document.querySelector('.answer');
    if(answer != null){answer.style["display"] = "none";}
    var message = document.querySelector('.show_massebereich');
    if(message != null){message.style["display"] = "none";}
    resetInterval = setInterval(function() {
        show_reset_progress(resetInterval); // so that the show_rest_progress-function can clear the intervall when needed
    }, 10000)
    document.querySelector('.progressbar').style["display"]= "flex"; 
    document.querySelector('.progress_message').style["display"]= "flex"; 
    $.ajax({
        type:'GET',
        url: "/webscraper/reset_database", //app_name(in urls.py):patern_name(in Dango, but here JavaScrips, because of that relative url)
        success:function(response){
            new_substances_loaded("DATABASE WAS COMPLETLY RESTORED");
            document.querySelector('.show_witz').style["display"]= "none";
        },
        error:function(){
            console.log("error ocoured");
        }
    });
}

async function load_new_substances() {
    changeBackground();
    try {
        const response = await $.ajax({
            type: 'GET',
            url: "webscraper/get_new_substances",
            timeout: 0
        });

        let message = "New Substances loaded:";
        for(url in response.newSubstances){
            message+= "\n"+response.newSubstances[url];
        }
        new_substances_loaded(message);
        changeBackground();
    } catch (error) {
        alert("not possible, try to reload whole db");
    }
}

function new_substances_loaded(message){
    
    document.querySelector(".container").style["background-color"] = "black";
    let show_message = document.createElement("div");
    show_message.setAttribute("id","message_bar");
    let skull_video = document.createElement("video");
    skull_video.setAttribute("id","skull_video");
    let message_div = document.createElement("div");
    message_div.setAttribute("id","message_div");
    let skull_source = document.createElement("source");
    skull_source.setAttribute("src","{% static 'videos/roboter.mp4' %}");
    skull_source.setAttribute("type","video/mp4");
    skull_video.append(skull_source);

    show_message.append(skull_video);
    skull_video.autoplay = true;
    skull_video.loop = true;
    let bring_message = document.createElement("div");
    bring_message.innerHTML = message;
    bring_message.setAttribute("id","bring_message");

    show_message.append(skull_video);
    
    let dismis = document.createElement("button");
    dismis.setAttribute("id","dismis_message");
    dismis.innerHTML="Dissmis Information";
    message_div.append(dismis);
    message_div.append(bring_message);
    document.querySelector(".container").append(show_message);
    document.querySelector(".container").append(message_div);
    setTimeout(function() {
        skull_video.style.display = "none";
        document.querySelector(".container").style["background-color"] = "transparent";
        show_message.style["display"] = "none";
    }, 1500);
    dismis.onclick=function(){
    message_div.remove();
    show_message.remove();
    };
}
document.querySelector('#search_field').addEventListener("focusout", ()=>{
    setTimeout(()=>$('#suggestionList').empty(),100);    
})

function displaySuggestions(suggestions) {
    $('#suggestionList').empty();
    for (var suggestion in suggestions) {
        var displayed_text = suggestions[suggestion];
        const sug = $('<div></div>');
        sug.text(displayed_text);
        sug.addClass("suggestionItem");
        sug.on("click", function(){
            var text = $(this).text();
            $('#search_field').val(text);
            $('#suggestionList').empty();
        })
        $('#suggestionList').append(sug);
    }
}


function generateJsonFile(){
try{
   $.ajax(
        {
            type: "GET",
            url:"webscraper/generate",
            success:function(response){
                var json_data = JSON.stringify(response)
    var blob = new Blob([json_data], {type: "application/json"})
    var url = URL.createObjectURL(blob)
    var a = document.createElement("a");
    a.style.display = "none";
    a.href = url;
    a.download = "PIHKAL.json"; 
    document.body.appendChild(a);
    a.click();

    document.body.removeChild(a);

    URL.revokeObjectURL(url);
            }
        }
    );
  

}catch(Exeption ){
    alert("This action isnt possible");
}
}
var drag_and_drop_is_active = false;
function proccesJsonFile(){
if(!drag_and_drop_is_active){
    drag_and_drop_is_active = true;
}else{
    drag_and_drop_is_active = false;
}if(drag_and_drop_is_active){
var drop_zone = document.createElement('div');
drop_zone.setAttribute('class', 'drop-zone');
drop_zone.setAttribute('id', 'drop-zone');
drop_zone.innerHTML="Drag and Drugs, Baby";
document.querySelector('.process').innerHTML="End Inserting";

drop_zone.addEventListener('dragover', (event)=>{
    event.preventDefault();
    drop_zone.classList.add('drag-over');
    console.log("dragover");
});
drop_zone.addEventListener('dragleave', (event)=>{
    drop_zone.classList.remove('drag-over');
    console.log("dragleave");

});
drop_zone.addEventListener('drop', (event)=>{
    event.preventDefault();
    drop_zone.classList.remove('drag-over');
    var file = event.dataTransfer.files[0];
    var csrfToken = $('[name="csrfmiddlewaretoken"]').val();

    const data = new FormData();
    data.append("csrfmiddlewaretoken", csrfToken);
    data.append("file", file);

    $.ajax({
        type:"POST",
        url:"webscraper/processJsonInput",
        data : data,
        processData:false,
        contentType: false,
        success:function(response){
            alert(file.name +" was tasty, thanks Buddy!!");
        },
        error:function(response){
            alert("File couldnt be stored");
        },
    })
});


document.querySelector('.container').append(drop_zone);
}
else{
document.querySelector('#drop-zone').remove();
document.querySelector('.process').innerHTML="Insert Data";

}
}
function get_search_category(){
return $('#select').val();
}
function get_what_is_searched(){
return $('#search_field').val();  }

const suggestions = []

function searchSuggestions(){
var category = get_search_category();
var what_is_searched = get_what_is_searched();

if((what_is_searched.length >= 2 && category!="molecular_mass" && category!="smiles" )|| (what_is_searched.length > 5 && category=="smiles") || category=="category"){
    data={
        category: category,
        searched: what_is_searched,
    }

    $.ajax({
        type:"GET",
        url:"webscraper/my_api",
        data:data,
        success:(response)=>{
            let suggestions = response;
            displaySuggestions(suggestions,category);
        },
        error:(response)=>{},
    })
}
}


function delete_search_results() {
console.log("Delete request made");
$.ajax({
    type: 'GET',
    url: "webscraper/delete_search_result",

    success: function(response) {
        alert("Delete request successful");
        // Hier kannst du die Antwort des Servers verarbeiten, wenn benötigt
    },
    error: function(xhr, status, error) {
        console.error("Error deleting search results:", error);
        // Hier kannst du auf einen Fehler reagieren, wenn benötigt
    }
});
}
