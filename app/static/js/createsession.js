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
    close = document.createElement('span')

    //setting attributes of elements
    if (target == 'pre'){
        question.setAttribute('class', 'preQ')
        close.setAttribute('id', 'preqD'+counter)
    }
    else{
        question.setAttribute('class', 'postQ')
        close.setAttribute('id', 'postD'+counter)
    }
    //question.setAttribute('class', 'question')
    close.textContent = 'X'
    close.setAttribute('class', 'del')
    //close.setAttribute('id', 'd'+counter)
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

//function to retrieve and submit results
function submit(){

    var prequestions = []
    var postquestions = []

    // retrieving title
    var title = document.getElementById('title').value

    // retrieving consent
    var consent = document.getElementById('consent').value

    // retrieving all prequestions
    var all = document.getElementsByClassName('preQ')
    //if there are no prequestions
    if (all == null){
        prequestions = []
    }
    else{
        for(let i = 0; i< all.length; i ++){
            //if question is mcq
            if(all[i].value.includes('\n')){
                var temp = all[i].value.split('\n')
                var question = temp[0]
                temp.shift()
                option = temp.join('\n')
                final = question + '\n' + option
            }
            //if question is open ended
            else{
                final = all[i].value
            }
            prequestions.push(final)
        }
    }
    console.log(typeof prequestions)


    // retrieving all emotions
    emotion = document.getElementById('emotion').value

    // retrieving all intensity
    intensity = parseInt(document.getElementById('intensity').value)
    console.log(Number.isInteger(intensity))

    // retrieving all post questions
    all = document.getElementsByClassName('postQ')
    for(let i = 0; i< all.length; i ++){
        postquestions.push(all[i].value)
    }
    console.log(postquestions)

    //combining the data
    mydata =  {
        sessionTitle:title, 
        consent: consent, 
        preQuestions: prequestions, 
        emotions: emotion, 
        intensity:intensity, 
        postQuestions:postquestions
    }
    console.log("DATA:",mydata)

    
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

}

