var counter = 2

//adding question block
function add(target) {
    counter++
    var close

    //retrieving parent div container
    if (target == 'pre') {
        parent = document.getElementById('pre_questions')
    }
    else {
        parent = document.getElementById('post_questions')
    }

    //creating necessary elements
    question = document.createElement('textarea')
    para = document.createElement('p')
    close = document.createElement('i')

    //setting attributes of elements
    if (target == 'pre') {
        question.setAttribute('class', 'preQ')
        close.setAttribute('id', 'preqD' + counter)
        para.setAttribute('id', 'preq_error' + counter)
    }
    else {
        question.setAttribute('class', 'postQ')
        close.setAttribute('id', 'postD' + counter)
        para.setAttribute('id', 'postq_error' + counter)
    }
    
    question.setAttribute('id', 't' + counter)
    para.setAttribute('class', 'error')
    close.setAttribute('class', 'fas fa-trash fa-2x')
    close.setAttribute('onclick', 'del(this)')

    //creating child to be appended into parent
    child = document.createElement('div')
    child.appendChild(question)
    child.appendChild(close)
    child.appendChild(para)
    child.setAttribute('id', counter)
    child.setAttribute('class', 'qblock')

    //adding child to parent
    parent.appendChild(child)
}

// delete question block
function del(x) {
    target = x.id.slice(-1)
    child = document.getElementById(target)

    //if target belongs to prequestions
    if (x.id.includes('pre')) {
        parent = document.getElementById('pre_questions')
    }
    //if target belongs to postquestions
    else {
        parent = document.getElementById('post_questions')
    }

    parent.removeChild(child)
}

//function to retrieve results
//title
function retrieve_title() {
    var title = document.getElementById('title').value.trim()
    return title
}
//consent
function retrieve_consent() {
    var consent = document.getElementById('consent').value.trim()
    return consent
}
//prequestions
function retrieve_questions(type) {

    var questions = []
    if (type == "pre"){
        var all = document.getElementsByClassName('preQ')
    }
    else {
        var all = document.getElementsByClassName('postQ')
    }
    //if there are no question
    if (all.length == 0) {
        questions = []
    }
    else {
        for (let i = 0; i < all.length; i++) {
            var question = all[i].value

            var temp2 = []
            // checking if theres a new line in question
            if (question.includes('\n')){
                var temp = question.split('\n')
                // check if option is uncessary 
                for (j = 0; j<temp.length; j++){
                    var option = temp[j]
                    if (option.replace(/ /g,'') != ""){
                        temp2.push(option)
                    }
                }
                if (temp2.length == 1){
                    questions.push(temp2[0].trim())
                }
                else{
                    var final = ''
                    for(x = 0; x<temp2.length; x++){
                        if(x == temp2.length -1){
                            final += temp2[x].trim()
                        }
                        else{
                            final += temp2[x].trim() + '\n'
                        }
                    }
                    questions.push(final)
                }
            }
            else{
                questions.push(question.trim())
            }
        }
    }
    final_questions = JSON.stringify(questions)
    return final_questions
}

//emotions
function retrieve_emotions(){
    emotions = document.getElementById('emotion').value
    var all = emotions.split('\n')
    var final = ""
    var temp = []
    // removing empty new lines
    for (i =0; i< all.length; i++){
        var emotion = all[i]
        if(emotion.replace(/ /g,'') != ""){
            temp.push(emotion)
        }
    }
    // checking number of emotions
    if (temp.length == 1){
        var final = temp[0].trim()
    }
    else{
        for (j = 0; j<temp.length; j++){
            if(j == temp.length -1){
                final += temp[j].trim()
            }
            else{
                final += temp[j].trim() + '\n'
            }

        }
    }
    return final
}

//intensity
function retrieve_intensity() {
    intensity = parseInt(document.getElementById('intensity').value)
    return intensity
}

// function to check if there is all input
function validateInput(){

    // retrieving input
    var title = document.getElementById('title').value
    var consent = document.getElementById('consent').value
    var emotions = document.getElementById('emotion').value
    var intensity = document.getElementById('intensity').value
    var all_pre = document.getElementsByClassName('preQ')
    var all_post = document.getElementsByClassName('postQ')

    // for title
    var title_input = document.getElementById('title')
    var title_label = document.getElementById('title_error')   
    if (title.replace(/ /g,'') == ""){
        title_label.innerHTML = "Please Enter a Title for your session!"
        title_label.style.visibility = 'visible'
        title_input.style.border = "solid red"
        test_title = false
    }
    else{
        title_label.style.visibility = 'hidden'
        title_input.style.border = "none"
        test_title = true
    }

    // for consent
    var consent_input = document.getElementById('consent')
    var consent_label = document.getElementById('consent_error')
    if (consent.replace(/ /g,'') == ""){   
        consent_label.innerHTML = "Please enter the Consent Agreement for your session!"
        consent_label.style.visibility = 'visible'
        consent_input.style.border = "solid red"
        test_consent = false
    }
    else{
        consent_label.style.visibility = 'hidden'
        consent_input.style.border = "none"
        test_consent = true
    }
    
    // for prequestion
    if (all_pre.length != 0){
        var temp = []
        for (i = 0; i<all_pre.length; i ++){
            var id = all_pre[i].id.split('t')[1]
            var pre_input = document.getElementById('t' + id)
            var pre_label = document.getElementById('preq_error' + id)
            if(all_pre[i].value.replace(/ /g,'') == ""){
                pre_label.innerHTML = "Please enter the Prequestion for your session!"
                pre_label.style.visibility = 'visible'
                pre_input.style.border = "solid red"
                temp.push(false)
            }
            else{
                pre_label.style.visibility = 'hidden'
                pre_input.style.border = "none"
                temp.push(true)
            }
        }
        if (temp.includes(false) == true){
            test_pre = false
        }
        else{
            test_pre = true
        }
    }
    else{
        test_pre = true
    }
    
    // for emotions
    var emotions_input = document.getElementById('emotion')
    var emotions_label = document.getElementById('emotions_error')
    if (emotions.replace(/ /g,'') == ""){
        
        emotions_label.innerHTML = "Please enter the Emotion(s) for your session!"
        emotions_label.style.visibility = 'visible'
        emotions_input.style.border = "solid red"
        test_emotions = false
    }
    else{
        emotions_label.style.visibility = 'hidden'
        emotions_input.style.border = "none"
        test_emotions = true
    }

    // for intensity
    var intensity_input = document.getElementById('intensity')
    var intensity_label = document.getElementById('intensity_error')
    if (intensity < 3 || intensity > 12){
        intensity_label.innerHTML = "Please enter a number from 3-12 as the Intensity for your session!"
        intensity_label.style.visibility = 'visible'
        intensity_input.style.border = "solid red"
        test_intensity = false
    }
    else{
        intensity_label.style.visibility = 'hidden'
        intensity_input.style.border = "none"
        test_intensity = true
    }

    // for postquestion
    if (all_post.length != 0){
        var temp = []
        for (i = 0; i<all_post.length; i ++){
            var id = all_post[i].id.split('t')[1]
            var post_input = document.getElementById('t' + id)
            var post_label = document.getElementById('postq_error' + id)
            if(all_post[i].value.replace(/ /g,'') == ""){
                post_label.innerHTML = "Please enter the Postquestion for your session!"
                post_label.style.visibility = 'visible'
                post_input.style.border = "solid red"
                temp.push(false)
            }
            else{
                post_label.style.visibility = 'hidden'
                post_input.style.border = "none"
                temp.push(true)
            }
        }
        if (temp.includes(false) == true){
            test_post = false
        }
        else{
            test_post = true
        }
    }
    else{
        test_post = true
    }

    if (test_title != null && test_consent != null && test_emotions != null &&  test_intensity == true && test_pre == true && test_post == true ){
        return true
    }
    else{
        return false
    }

}

//function to retrieve and submit results
function submit() {

    // validate input
    var validation = validateInput()
    if (validation == true){

        //retrieving results
        var title = retrieve_title()
        var consent = retrieve_consent()
        var prequestions = retrieve_questions('pre')
        var emotion = retrieve_emotions()
        var intensity = retrieve_intensity()
        var postquestions = retrieve_questions('post')

        //combining the data
        mydata = {
            sessionTitle: title,
            consent: consent,
            preQuestions: prequestions,
            emotions: emotion,
            intensity: intensity,
            postQuestions: postquestions
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
}



function hide() {
    $('#myModal').modal('hide')
}
