// Select clicked image and display match info. after waiting 2s for html refreshing (render_template)
d3.selectAll(".col-2").on('click', setTimeout(matchDisplay(), 2000));

/**
 * Flask returns data of matches to "prediction.html". 
 * Use internal javascript to retrieve such data and display them on "prediction.html"
 */
function matchDisplay() {

    // Retrieve league info (as string)
    let league = data.split('{&#39;League&#39;: &#39;')[1].split("&#39;")[0];

    // Object to hold match info
    matchObj = {};

    // Column names to be shown in "prediction.html"
    let cols = ["Home", "Away", "Company", "Pred_W (ct)", "Pred_D (ct)", "Pred_L (ct)", "Result"];

    // Assign keys to "matchObj" (type of values as array)
    cols.forEach((col) => matchObj[col] = []);

    // Use "keys" of data string to determine total matches to be displayed
    let totalMatches = data.split("match").length - 1;

    // Note that matches may not get prediction on all "W", "D", and "L"
    // As a result, isolate info. for each match so that empty string functions as placeholder in "matchObj"
    for (let i = 0; i < totalMatches; i++) {

        // Split original data to get rid of info. to the left of iterated match
        split_im = data.split(`&#39;match${i}&#39;: `)[1];
        // Further split to get rid of info. to the right of iterated match
        match_info = split_im.split(`&#39;match${i + 1}&#39;: `)[0];

        // Split and store data of match info in "matchArr"
        let matchArr = match_info.split('&#39;').filter((ele) => !["{", ": ", ": {", ", "].includes(ele));

        // Clean "matchArr"
        for (let i = 0; i < matchArr.length; i++) {

            if (matchArr[i].slice(0, 2) === ": ") {
                matchArr[i] = matchArr[i].slice(2);
            }
            if (matchArr[i].slice(-2) === ", ") {
                matchArr[i] = matchArr[i].slice(0, -2)
            }
            if (matchArr[i].slice(-1) === "}") {
                matchArr[i] = matchArr[i].slice(0, -1)
            } 

        }

        // Remove "}" from the last element of "matchArr"
        if (i === totalMatches - 1) matchArr.push(matchArr.pop().slice(0, -1));

        // Append match info to "matchObj"
        cols.forEach((col) => {

            // Append values if iterated column exist in match
            if (matchArr.includes(col)) {

                for (let i = 0; i < matchArr.length; i ++) {
                    if (matchArr[i] === col) {
                        matchObj[col].push(matchArr[i + 1]);
                    }
                }                
            
            // Append empty string if iterated column does not exist
            } else {
                matchObj[col].push("");
            }    

        });    
    }   

    // Remove title for existing predicted result
    d3.select(".pred-title").remove();

    // Add new title for predicted result
    d3.select("#pred-info")
        .append('p')
        .attr("class", "pred-title mb-5")
        .text("Prediction results for");

    /**
     * Return color code corresponding to the background of league in "prediction.html"
     * @param {*} league Name of league, STRING datatype
     */
        function leagueColor(league) {

        return league === "PremierLeague" ? "C-00FFFF" :
                league === "LaLiga" ? "C-FF66FF" :
                league === "Bundesliga" ? "C-F7DE00" :
                league === "Serie-A" ? "C-FF9900" :
                league === "Ligue1" ? "C-FF0000" :
                league === "MLS" ? "C-00FF00" : "C-000000";

    }

    // Retrieve color code for selected league
    let color = leagueColor(league)

    // Append league name and color code for title of prediction on "prediction.html"
    d3.select(".pred-title")
        .append('p')
        .attr("class", `${color}`)
        .text(`${league}`);

    // Remove pre-existing table
    d3.select("table").remove();

    // Append header of tbody
    let tbody = d3.select("#pred-table")
        .append("table")
        .attr("class", "temporary-table")
        .append("tbody");
    // Append "tr" for "th"
    let trHeader = tbody.append("tr")
        .attr("class", "py-5");
    // Append "th"
    cols.forEach((col) =>{
        trHeader.append("td")
            .text(col);
    });

    // Append data of tbody
    for (let i = 0; i < totalMatches; i++) {

        let tr = d3.select('tbody')
            .append('tr')
            .attr("class", "py-5");

        cols.forEach((col) => {

            if (col === "Home" || col === "Away") {
                tr.append('td')
                    .append('img')
                    .attr("src", `../static/image/icons/${league}/${matchObj[col][i]}.png`)
                    .attr("class", "py-2");

            } else {
                tr.append('td')
                    .text(matchObj[col][i]);
            }

        });

    }
}