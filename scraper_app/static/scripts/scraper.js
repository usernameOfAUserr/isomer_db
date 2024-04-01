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
function selectFunction(resetInterval){
let select = document.querySelector('#select');
let value = select.value;
if (value=="massebereich"){
    let abweichung = document.querySelector('#abweichung');
    abweichung.style["display"] = "block";
}
if(value != "massebereich"){
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
                show_witz.style["display"] = "none";
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
        },
        error:function(){
            console.log("error ocoured");
        }
    });
}

function load_new_substances(){
    changeBackground();
    $.ajax({
        type:'GET',
        url: "webscraper/get_new_substances",
        timeout: 0,
        success:function(response){
            alert("New Substances loaded");
            for (url in response.newSubstances){
                alert(response.newSubstances[smile])
            }
            changeBackground();
        },
        error:function(){
            alert("not possible, try to reload whole db");
        },
    });
}