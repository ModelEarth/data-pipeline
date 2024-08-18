async function getCountyChart(chartVariable, entityId, showAll, chartText) {
    // Fetch all geoIds for counties
    const response = await fetch(`https://api.datacommons.org/v2/observation?key=AIzaSyCTI4Xz-UW_G2Q2RfknhcfdAnTHq5X5XuI&entity.expression=${entityId}%3C-containedInPlace%2B%7BtypeOf%3ACounty%7D&select=date&select=entity&select=value&select=variable&variable.dcids=${chartVariable}`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({
            "dates": ""
        })
    });
    const data = await response.json();

    // Use the geoId list to fetch respective county + state names
    const geoIds = Object.keys(data.byVariable[chartVariable].byEntity);
    const response2 = await fetch('https://api.datacommons.org/v2/node?key=AIzaSyCTI4Xz-UW_G2Q2RfknhcfdAnTHq5X5XuI', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({
            "nodes": geoIds,
            "property": "->[containedInPlace, name]"
        })
    });
    const data2 = await response2.json();

    // Put county info together
    const countyData = {};
    Object.keys(data2.data).forEach(geoId => {
        node = data2.data[geoId].arcs;
        stateName = node.containedInPlace.nodes[0]['name'];
        countyName = node.name.nodes[0]['value'];
        countyData[geoId] = {
            name: countyName,
            state: stateName
        };
    })

    // Fetch observational data using geoIds list
    const url = `https://api.datacommons.org/v2/observation?key=AIzaSyCTI4Xz-UW_G2Q2RfknhcfdAnTHq5X5XuI&variable.dcids=${chartVariable}&${geoIds.map(id => `entity.dcids=${id}`).join('&')}`
    const response3 = await fetch(url, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({
            "date": "",
            "select": ["date", "entity", "value", "variable"]
        })
    })
    const data3 = await response3.json();

    // Format data
    const formattedData = [];
    for (const geoId in countyData) {
        formattedData.push({
            county: `${countyData[geoId].name}, ${countyData[geoId].state}`,
            observations: data3.byVariable[chartVariable].byEntity[geoId].orderedFacets[0]['observations']
        })
    }

    // Get unique years
    let yearsSet = new Set();
    formattedData.forEach(county => {
        county.observations.forEach(obs => {
            yearsSet.add(obs.date);
        });
    });
    const years = [...yearsSet].sort((a, b) => a - b);
    
    // Showing all or top 5 or bottom 5 counties
    let selectedData;
    formattedData.forEach(county => {
        county.averageLandCover = county.observations.reduce((sum, obs) => sum + obs.value, 0) / county.observations.length;
    });
    if (showAll == 'showTop5') {
        selectedData = formattedData.sort((a, b) => b.averageLandCover - a.averageLandCover).slice(0, 5);
    } 
    else if (showAll == 'showBottom5') {
        selectedData = formattedData.sort((a, b) => a.averageLandCover - b.averageLandCover).slice(0, 5);
    }
    else {
        selectedData = formattedData;
    }

    // Get datasets
    const datasets = selectedData.map(county => {
        return {
            label: county.county,
            data: years.map(year => {
                const observation = county.observations.find(obs => obs.date === year);
                return observation ? observation.value : null;
            }),
            borderColor: 'rgb(' + Math.floor(Math.random() * 256) + ', ' + Math.floor(Math.random() * 256) + ', ' + Math.floor(Math.random() * 256) + ')',
            backgroundColor: 'rgba(0, 0, 0, 0)',
        };
    });

    const config = {
        type: 'line',
        data: {
            labels: years,
            datasets: datasets
        },
        options: {
            responsive: true,
            plugins: {
                legend: {
                    position: 'top',
                },
                title: {
                    display: true,
                    text: chartText
                }
            },
            scales: {
                x: {
                    title: {
                        display: true,
                        text: 'Year'
                    }
                },
                y: {
                    title: {
                        display: true,
                        text: chartText
                    }
                }
            }
        }
    };

    // Delete chart if it already exists
    if (countyChart instanceof Chart) {
        countyChart.destroy();
    }
    const ctx = document.getElementById('countyChart').getContext('2d');
    countyChart = new Chart(ctx, config);
}

document.addEventListener('DOMContentLoaded', () => {
    let chartVariable = 'Count_Person';
    let showAll = 'showTop5';
    let entityId = 'geoId/01'
    let chartText = document.getElementById('chartVariable').options[document.getElementById('chartVariable').selectedIndex].text;

    getCountyChart(chartVariable, entityId, showAll, chartText);

    document.forms['countyShow'].addEventListener('change', function(event) {
        if (event.target.name === 'countyShow') {
            showAll = document.querySelector('input[name="countyShow"]:checked').value;
            getCountyChart(chartVariable, entityId, showAll, chartText);
        }
    });

    document.getElementById('chartVariable').addEventListener('change', (event) => {
        chartVariable = event.target.value;
        chartText = document.getElementById('chartVariable').options[document.getElementById('chartVariable').selectedIndex].text;
        getCountyChart(chartVariable, entityId, showAll, chartText);
    });

    document.getElementById('entityId').addEventListener('change', (event) => {
        entityId = event.target.value;
        getCountyChart(chartVariable, entityId, showAll, chartText);
    });
});

async function getCountryChart(chartVariable, facetId) {
    // Get countries from URL
    const currentUrl = window.location.href;
    const equalParams = currentUrl.split('='); 
    const countryParams = equalParams[equalParams.length - 1];
    let selectedCountries = countryParams.split(',');

    // Fetch country codes for selected countries
    const response = await fetch('https://api.datacommons.org/v2/resolve?key=AIzaSyCTI4Xz-UW_G2Q2RfknhcfdAnTHq5X5XuI', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({
            "nodes": selectedCountries,
            "property": "<-description{typeOf:Country}->dcid"
        })
    });
    const data = await response.json();

    // Make a dictionary of country code -> name
    const countryCodes = {};
    data.entities.forEach(entity => {
        if (entity.node && entity.candidates && entity.candidates[0] && entity.candidates[0].dcid) {
            countryCodes[entity.candidates[0].dcid] = entity.node;
        }
    });

    // Fetch data for selected countries and selected variable
    const geoIds = Object.keys(countryCodes);
    const url = `https://api.datacommons.org/v2/observation?key=AIzaSyCTI4Xz-UW_G2Q2RfknhcfdAnTHq5X5XuI&variable.dcids=${chartVariable}&${geoIds.map(id => `entity.dcids=${id}`).join('&')}`
    const response2 = await fetch(url, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({
            "date": "",
            "select": ["date", "entity", "value", "variable"]
        })
    })
    const data2 = await response2.json();

    // There's many sources of data so we need to choose one data source and its corresponding facetId
    // let facetId = "3981252704"; 
    // for (const facetIdCheck in data2.facets) {
    //     if (data2.facets[facetIdCheck].provenanceUrl === "https://datacatalog.worldbank.org/dataset/world-development-indicators/") {
    //         facetId = facetIdCheck;
    //     }
    // }

    // Use facetId to build formatted data
    const formattedData = []
    for (const geoId of geoIds) {
        formattedData.push({
            country: countryCodes[geoId],
            observations: data2.byVariable[chartVariable].byEntity[geoId].orderedFacets.find((element) => element.facetId == facetId)['observations']
        })
    }

    // Get unique years
    let yearsSet = new Set();
    formattedData.forEach(country => {
        country.observations.forEach(obs => {
            yearsSet.add(obs.date);
        });
    });
    const years = [...yearsSet].sort((a, b) => a - b);

    // Get datasets
    const datasets = formattedData.map(country => {
        return {
            label: country.country,
            data: years.map(year => {
                const observation = country.observations.find(obs => obs.date === year);
                return observation ? observation.value : null;
            }),
            borderColor: 'rgb(' + Math.floor(Math.random() * 256) + ', ' + Math.floor(Math.random() * 256) + ', ' + Math.floor(Math.random() * 256) + ')',
            backgroundColor: 'rgba(0, 0, 0, 0)',
        };
    });

    const config = {
        type: 'line',
        data: {
            labels: years,
            datasets: datasets
        },
        options: {
            responsive: true,
            plugins: {
                legend: {
                    position: 'top',
                },
                title: {
                    display: true,
                    text: 'Population'
                }
            },
            scales: {
                x: {
                    title: {
                        display: true,
                        text: 'Year'
                    }
                },
                y: {
                    title: {
                        display: true,
                        text: 'Population'
                    }
                }
            }
        }
    };

    // Delete chart if it already exists
    if (countryChart instanceof Chart) {
        countryChart.destroy();
    }
    const ctx = document.getElementById('countryChart').getContext('2d');
    countryChart = new Chart(ctx, config);

    // Use the following to track hash changes -
    // document.addEventListener('hashChangeEvent', () => {
    //    chartVariable = 'Count_Person';
    //    facetId = '3981252704';
    //    getCountryChart(chartVariable, facetId);
    // })
}

document.addEventListener('DOMContentLoaded', () => {
    getCountryChart('Count_Person', '3981252704');
})

document.addEventListener('hashChangeEvent', () => {
    console.log('check');
    getCountryChart('Count_Person', '3981252704');
})

async function getStateChart(chartVariable, statesList, facetId) {
    // For US States only
    // Fetch geoIds of all given states
    const response = await fetch('https://api.datacommons.org/v2/resolve?key=AIzaSyCTI4Xz-UW_G2Q2RfknhcfdAnTHq5X5XuI', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({
            "nodes": statesList,
            "property": "<-description{typeOf:State}->dcid"
        })
    });
    const data = await response.json();
    
    // Make a dictionary of state code -> name
    const stateCodes = {};
    data.entities.forEach(entity => {
        if (entity.node && entity.candidates && entity.candidates[0] && entity.candidates[0].dcid) {
            stateCodes[entity.candidates[0].dcid] = entity.node;
        }
    });

    // Fetch data for states and selected variable
    const geoIds = Object.keys(stateCodes);
    const url = `https://api.datacommons.org/v2/observation?key=AIzaSyCTI4Xz-UW_G2Q2RfknhcfdAnTHq5X5XuI&variable.dcids=${chartVariable}&${geoIds.map(id => `entity.dcids=${id}`).join('&')}`
    const response2 = await fetch(url, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({
            "date": "",
            "select": ["date", "entity", "value", "variable"]
        })
    })
    const data2 = await response2.json();
    
    // Use facetId to build formatted data
    const formattedData = []
    for (const geoId of geoIds) {
        formattedData.push({
            state: stateCodes[geoId],
            observations: data2.byVariable[chartVariable].byEntity[geoId].orderedFacets.find((element) => element.facetId == facetId)['observations']
        })
    }

    // Get unique years
    let yearsSet = new Set();
    formattedData.forEach(state => {
        state.observations.forEach(obs => {
            yearsSet.add(obs.date);
        });
    });
    const years = [...yearsSet].sort((a, b) => a - b);
    console.log(years);

    // Get datasets
    const datasets = formattedData.map(state => {
        return {
            label: state.state,
            data: years.map(year => {
                const observation = state.observations.find(obs => obs.date === year);
                return observation ? observation.value : null;
            }),
            borderColor: 'rgb(' + Math.floor(Math.random() * 256) + ', ' + Math.floor(Math.random() * 256) + ', ' + Math.floor(Math.random() * 256) + ')',
            backgroundColor: 'rgba(0, 0, 0, 0)',
        };
    });
    
    const config = {
        type: 'line',
        data: {
            labels: years,
            datasets: datasets
        },
        options: {
            responsive: true,
            plugins: {
                legend: {
                    position: 'top',
                },
                title: {
                    display: true,
                    text: 'Population'
                }
            },
            scales: {
                x: {
                    title: {
                        display: true,
                        text: 'Year'
                    }
                },
                y: {
                    title: {
                        display: true,
                        text: 'Population'
                    }
                }
            }
        }
    };

    // Delete chart if it already exists
    if (stateChart instanceof Chart) {
        stateChart.destroy();
    }
    const ctx = document.getElementById('stateChart').getContext('2d');
    stateChart = new Chart(ctx, config);
}

document.addEventListener('DOMContentLoaded', () => {
    chartVariable = 'Count_Person';
    statesList = ['Florida', 'New Jersey', 'New York State', 'New Mexico', 'Alaska']; // 'New York' does not work, use 'New York State' - idk why
    facetId = '2176550201';
    getStateChart(chartVariable, statesList, facetId);
})