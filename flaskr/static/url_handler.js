function feed_url(url){
    var url_input = document.getElementById('url_input')
    var url = url_input.value

    console.log("Feeding crawler with ", url)
    var xhr = new XMLHttpRequest()
    // verify URL by regex
    const data = {
        'url': url
    }
    xhr.open('post', 'crawl_cnn')
    xhr.setRequestHeader('Content-Type', 'application/json;charset=UTF-8')
    xhr.onreadystatechange = function() {
        if (xhr.readyState === 3){
            //Loading
        }
        if (xhr.readyState === 4){
            alert(xhr.responseText)
        }
    }

    xhr.send(JSON.stringify(data))
}
