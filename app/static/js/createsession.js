var counter = 1

//adding question block
function add(){
    counter ++
    var close

    //retrieving parent div container
    parent = document.getElementById('questions')
    
    //creating necessary elements
    question = document.createElement('textarea')
    close = document.createElement('span')

    //setting attributes of elements
    question.setAttribute('class', 'question')
    close.textContent = 'X'
    close.setAttribute('class', 'del')
    close.setAttribute('id', 'd'+counter)
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
    parent = document.getElementById('questions')

    parent.removeChild(child)
}

//function to retrieve and submit results
function submit(){

    var prequestions = []

    // retrieving title
    title = document.getElementById('title').value

    // retrieving consent
    consent = document.getElementById('consent').value

    // retrieving all prequestions
    all = document.getElementsByClassName('question')
    for(let i = 0; i< all.length; i ++){
        //if question is mcq
        if(all[i].value.includes('\n')){
            temp = all[i].value.split('\n')
            question = temp[0]
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