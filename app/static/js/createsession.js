var counter = 2

//adding question block
function add(target){
    counter ++
    var close

    //retrieving parent div container
    if (target == 'pre'){
        parent = document.getElementById('pre_questions')
    }
    else{
        parent = document.getElementById('post_questions')
    }
    
    //creating necessary elements
    question = document.createElement('textarea')
    close = document.createElement('i')

    //setting attributes of elements
    if (target == 'pre'){
        question.setAttribute('class', 'preQ')
        close.setAttribute('id', 'preqD'+counter)
    }
    else{
        question.setAttribute('class', 'postQ')
        close.setAttribute('id', 'postD'+counter)
    }
    close.setAttribute('class', 'fas fa-trash fa-2x')
    close.setAttribute('onclick', 'del(this)')

    //creating child to be appended into parent
    child = document.createElement('div')
    child.appendChild(question)
    child.appendChild(close)
    child.setAttribute('id', counter)
    child.setAttribute('class', 'qblock')

    //adding child to parent
    parent.appendChild(child)
}

// delete question block
function del(x){
    target = x.id.slice(-1)
    child = document.getElementById(target)
    
    //if target belongs to prequestions
    if(x.id.includes('pre')){
        parent = document.getElementById('pre_questions')
    }
    //if target belongs to postquestions
    else{
        parent = document.getElementById('post_questions')
    }
    
    parent.removeChild(child)
}

//function to retrieve results
//title
function retrieve_title(){
    var title = document.getElementById('title').value
    return title
}
//consent
function retrieve_consent(){
    var consent = document.getElementById('consent').value
    return consent
}
//prequestions
function retrieve_prequestions(){
    var prequestions = []
    var all = document.getElementsByClassName('preQ')
    //if there are no prequestions
    if (all == null){
        prequestions = []
    }
    else{
        for(let i = 0; i< all.length; i ++){
            var question = all[i].value.replace(/\n/g, "\\n")
            prequestions.push(question)
        }
    }
    jsonPreQ =JSON.stringify(prequestions)
    return jsonPreQ
}
//emotions
function retrieve_emotions(){
    emotion = document.getElementById('emotion').value.replace(/\n/g, "\\n")
    return emotion
}
//intensity
function retrieve_intensity(){
    intensity = parseInt(document.getElementById('intensity').value)
    return intensity
}

//post questions
function retrieve_postquestions(){
    var postquestions = []
    var all = document.getElementsByClassName('postQ')
    for(let i = 0; i< all.length; i ++){
        var question = all[i].value.replace(/\n/g, "\\n")
        postquestions.push(question)
    }
    jsonPostq = JSON.stringify(postquestions)
    return jsonPostq
}

//function to retrieve and submit results
function submit(){

    //retrieving results
    var title = retrieve_title()
    var consent = retrieve_consent()
    var prequestions = retrieve_prequestions()
    var emotion = retrieve_emotions()
    var intensity = retrieve_intensity()
    var postquestions = retrieve_postquestions()
    //combining the data
    mydata =  {
        sessionTitle:title, 
        consent: consent, 
        preQuestions: prequestions, 
        emotions: emotion, 
        intensity:intensity, 
        postQuestions:postquestions
    }
    //submiting data
    var xhttp = new XMLHttpRequest();
    xhttp.onreadystatechange = function () {

        if (xhttp.readyState === XMLHttpRequest.DONE) {
            const status = xhttp.status;
            if (status === 0 || (status >= 200 && status < 400)) {
                // The request has been completed successfully
                console.log('Submitted!')
                console.log(xhttp.responseText);
            } else {
                console.log(xhttp.responseText);
                // Oh no! There has been an error with the request!
            }
        }
    }
    xhttp.open('POST', '/createsession', true);
    xhttp.setRequestHeader('Content-Type', 'application/json');
    xhttp.send(JSON.stringify(mydata)); 

    //displaying modal
    $('#myModal').modal('show')
}

function hide(){
    $('#myModal').modal('hide')
}
