function sendData(e){
    e.preventDefault(); 


    var inputData = document.getElementById('search').value;

    var data = {
        inputText:inputData
    }

    var formData = new FormData()

    formData.append('inputText',data.inputText)

    console.log(inputData);
    // console.log(inputData);


    // var data = {
    //     'inputText': inputText
    // };
    $.ajax({
        url: 'http://127.0.0.1:5000/recommend/',
        type: 'POST',
        data: formData,
        processData: false,
        contentType: false,
        success: function(response) {
            // Handle the response and display the recommendation results
            displayRecommendationResults(response);
        },
        error:function(error){
            console.log("Error => ", error);
        }

    });
}


function displayRecommendationResults(response){
    var resultsContainer = document.getElementById('result');
    resultsContainer.innerHTML = ''; 

    // console.log(response.body)

    var res = response.body

    for(var i = 0 ; i < res.length ; i++){
        // console.log(res[i])

        var arr_data = res[i][0]
        // console.log(arr_data)
        var itemHtml = '<div class="recommendation-item">' +
                '<h3 class="title">' + arr_data[0] + '</h3>' +
                '<div class="detail">' +
                'Genre: ' + arr_data[1] + '<br>' +
                'Rating: ' + arr_data[2] + '<br>' +
                'Studio: ' + arr_data[3] + '<br>' +
                'Type: ' + arr_data[4] + '<br>' +
                '</div>' +
                '</div>';

        resultsContainer.innerHTML += itemHtml;

    }
    // if(response.status === 200){

    //     console.log(response)
    // }
}


var form = document.getElementById('recommendationForm');
form.addEventListener('submit', sendData);