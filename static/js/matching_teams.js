const MongoClient = require('mongodb').MongoClient;
const url = "http://mongodb://localhost:27017/Odds";

// Select clicked image
d3.selectAll(".league").on('click', function() {

    let matches = {};

    MongoClient.connect(url, function(err, db) {

        if (err) throw err;
        
        db.collection("query_im").find_one().toObject(function(err, result) {
            if (err) throw err;

            matches = result;

            db.close();
        });

    });

    let data = matches["match"],
    league = matches["league"];
  
    // Remove pre-existing table
    d3.select("table").remove();

    // Append header of tbody
    let tbody = d3.select("#pred")
        .append("table")
        .attr("class", "temporary-table")
        .append("tbody");
    // Re-order column names of the table
    let titleArrange = ["Home", "Away", "Company", "Pred_ct_W", "Pred_ct_D", "Pred_ct_L", "Result"];
    // Append "tr" for "th"
    let trHeader = tbody.append("tr")
                        .attr("class", "py-5");
    // Append "th"
    titleArrange.forEach((col) =>{
        trHeader.append("td")
        .text(col);
    });
    console.log(data);
    console.log(Object.values(data));


    Object.values(data).forEach((match) => {

        let tr = d3.select("tbody")
                    .append("tr")
                    .attr("class", "py-5");

        for (let col of titleArrange) {

            if (col === "Home") {
                tr.append("img")
                    .attr("src", `../static/image/icons/${league}/${match[col]}.png`)
            } else if (col === "Away") {
                tr.append("img")
                    .attr("src", `../static/image/icons/${league}/${match[col]}.png`)
            } else {
                tr.append("td")
                    .text(match[col]);
            }
        }
    });

});





    // d3.json("/output", function(matches) {

    //     let data = matches["match"],
    //         league = matches["league"];

    //     console.log(league);
        
            
    //     // Remove pre-existing table
    //     d3.select("table").remove();

    //     // Append header of tbody
    //     let tbody = d3.select("#pred")
    //         .append("table")
    //         .attr("class", "temporary-table")
    //         .append("tbody");
    //     // Re-order column names of the table
    //     let titleArrange = ["Home", "Away", "Company", "Pred_ct_W", "Pred_ct_D", "Pred_ct_L", "Result"];
    //     // Append "tr" for "th"
    //     let trHeader = tbody.append("tr")
    //                         .attr("class", "py-5");
    //     // Append "th"
    //     titleArrange.forEach((col) =>{
    //         trHeader.append("td")
    //         .text(col);
    //     });
    //     console.log(data);
    //     console.log(Object.values(data));
        

    //     Object.values(data).forEach((match) => {

    //         let tr = d3.select("tbody")
    //                     .append("tr")
    //                     .attr("class", "py-5");

    //         for (let col of titleArrange) {

    //             if (col === "Home") {
    //                 tr.append("img")
    //                     .attr("src", `../static/image/icons/${league}/${match[col]}.png`)
    //             } else if (col === "Away") {
    //                 tr.append("img")
    //                     .attr("src", `../static/image/icons/${league}/${match[col]}.png`)
    //             } else {
    //                 tr.append("td")
    //                     .text(match[col]);
    //             }
    //         }
    //     });


//     });

// });




    

//     // Connect to "/prediction" route of "app.py" to retrieve predicted data
//     d3.json("/league").then((data) => {
//         console.log(data);
        
//         // Remove pre-existing table
//         d3.select("table").remove();

//         // Append header of tbody
//         let tbody = d3.select("#pred")
//             .append("table")
//             .attr("class", "temporary-table")
//             .append("tbody");
//         // Re-order column names of the table
//         let titleArrange = ["Home", "Away", "Company", "Pred_ct_W", "Pred_ct_D", "Pred_ct_L", "Result"];
//         // Append "tr" for "th"
//         let trHeader = tbody.append("tr")
//                             .attr("class", "py-5");
//         // Append "th"
//         titleArrange.forEach((col) =>{
//             trHeader.append("td")
//             .text(col);
//         });
//         console.log(data);
//         console.log(Object.values(data));
        

//         Object.values(data).forEach((match) => {

//             let tr = d3.select("tbody")
//                         .append("tr")
//                         .attr("class", "py-5");

//             for (let col of titleArrange) {

//                 if (col === "Home") {
//                     tr.append("img")
//                         .attr("src", `../static/image/icons/${this.alt}/${match[col]}.png`)
//                 } else if (col === "Away") {
//                     tr.append("img")
//                         .attr("src", `../static/image/icons/${this.alt}/${match[col]}.png`)
//                 } else {
//                     tr.append("td")
//                         .text(match[col]);
//                 }
//             }
//         });
            
            
        
//     });


    


// });



    
    


    


