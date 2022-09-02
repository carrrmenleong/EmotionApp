var counter = 1

//adding question block
function add(){
    counter ++

    //retrieving parent div container
    parent = document.getElementById('questions')
    
    //creating necessary elements
    question = document.createElement('textarea')
    close = document.createElement('span')

    //setting attributes of elements
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
    console.log("SUCCESS")

    title = document.getElementById('title').value
    console.log(title)
}