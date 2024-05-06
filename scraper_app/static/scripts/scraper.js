document.addEventListener("DOMContentLoaded",function(){
    var select = document.getElementById('select');
  
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
                 var show_witz = document.querySelector('.show_witz')
                 show_witz.style['display'] = "none";
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


