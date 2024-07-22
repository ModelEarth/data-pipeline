async function fetchCountyGeoIds(graphVariable, entityId) {
    // Fetch all geoIds containing geoId/06 in name + are counties
    const response = await fetch(`https://api.datacommons.org/v2/observation?key=AIzaSyCTI4Xz-UW_G2Q2RfknhcfdAnTHq5X5XuI&entity.expression=${entityId}%3C-containedInPlace%2B%7BtypeOf%3ACounty%7D&select=date&select=entity&select=value&select=variable&variable.dcids=${graphVariable}`, {
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
    const geoIds = Object.keys(data.byVariable[graphVariable].byEntity);
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

    // Put data together
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
    return countyData;
}

async function fetchDataPoints(geoIds, graphVariable) {
    // Fetch data using geoIds list
    // TODO - Figure out how to put variable.dcids and entity.dcids in the body section instead of URL
    const url = `https://api.datacommons.org/v2/observation?key=AIzaSyCTI4Xz-UW_G2Q2RfknhcfdAnTHq5X5XuI&variable.dcids=${graphVariable}&${geoIds.map(id => `entity.dcids=${id}`).join('&')}`
    const response = await fetch(url, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({
            "date": "",
            "select": ["date", "entity", "value", "variable"]
        })
    })
    const data = await response.json();
    return data;
}

async function getFormattedData(graphVariable, entityId) {
    const geoIdsData = await fetchCountyGeoIds(graphVariable, entityId);
    const geoIds = Object.keys(geoIdsData);
    const forestCoverageData = await fetchDataPoints(geoIds, graphVariable);

    const formattedData = [];
    for (const geoId in geoIdsData) {
        formattedData.push({
            county: `${geoIdsData[geoId].name}, ${geoIdsData[geoId].state}`,
            observations: forestCoverageData.byVariable[graphVariable].byEntity[geoId].orderedFacets[0]['observations']
        })
    }
    return formattedData;
}

document.addEventListener('DOMContentLoaded', () => {
    const selectElement = document.getElementById('graphVariable');
    const h2Element = document.querySelector('h2');
    let graphVariable = 'LandCoverFraction_Forest';
    let showAll = false;
    let entityId = 'geoId/06'
    let myChart;

    // Function to update the H2 tag text and chart title
    const updateTexts = () => {
        const selectedOptionText = selectElement.options[selectElement.selectedIndex].text;
        h2Element.textContent = `${selectedOptionText} - Top 5 Counties`;
        if (myChart) {
            myChart.options.plugins.title.text = `${selectedOptionText} - Top 5 Counties`;
            myChart.update();
        }
    };

    async function getGraph(showAll, graphVariable, entityId) {
        const data = await getFormattedData(graphVariable, entityId);

        // Get unique years
        let yearsSet = new Set();
        data.forEach(county => {
            county.observations.forEach(obs => {
                yearsSet.add(obs.date);
            });
        });
        const years = [...yearsSet];
        
        // Showing all counties or top 5 counties only
        let selectedData;
        if (showAll) {
            selectedData = data;
        } else {
            data.forEach(county => {
                county.averageLandCover = county.observations.reduce((sum, obs) => sum + obs.value, 0) / county.observations.length;
            });
            selectedData = data.sort((a, b) => b.averageLandCover - a.averageLandCover).slice(0, 5);
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
                        text: `${selectElement.options[selectElement.selectedIndex].text} - Top 5 Counties`
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
                            text: `${selectElement.options[selectElement.selectedIndex].text}`
                        }
                    }
                }
            }
        };

        // Delete chart if it already exists
        if (myChart instanceof Chart) {
            myChart.destroy();
        }
        const ctx = document.getElementById('myChart').getContext('2d');
        myChart = new Chart(ctx, config);
    }

    updateTexts();
    getGraph(showAll, graphVariable, entityId);

    document.getElementById('showAllToggle').addEventListener('change', (event) => {
        showAll = event.target.checked;
        getGraph(showAll, graphVariable, entityId);
    });

    document.getElementById('graphVariable').addEventListener('change', (event) => {
        graphVariable = event.target.value;
        updateTexts();
        getGraph(showAll, graphVariable, entityId);
    });

    document.getElementById('entityId').addEventListener('change', (event) => {
        entityId = event.target.value;
        getGraph(showAll, graphVariable, entityId);
    });
});

async function getCountryGraph(graphVariable, selectedCountries) {
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
    const url = `https://api.datacommons.org/v2/observation?key=AIzaSyCTI4Xz-UW_G2Q2RfknhcfdAnTHq5X5XuI&variable.dcids=${graphVariable}&${geoIds.map(id => `entity.dcids=${id}`).join('&')}`
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

    // Get facetId based on a selected source
    let facetId = "3981252704"; // this is the facetId for the URL below, feels unsafe to have this hardcoded - check later
    for (const facetIdCheck in data2.facets) {
        if (data2.facets[facetIdCheck].provenanceUrl === "https://datacatalog.worldbank.org/dataset/world-development-indicators/") {
            facetId = facetIdCheck;
        }
    }

    // Use facetId to build formatted data
    const formattedData = []
    for (const geoId of geoIds) {
        formattedData.push({
            country: countryCodes[geoId],
            observations: data2.byVariable[graphVariable].byEntity[geoId].orderedFacets.find((element) => element.facetId == facetId)['observations']
        })
    }

    // Get unique years
    let yearsSet = new Set();
    formattedData.forEach(country => {
        country.observations.forEach(obs => {
            yearsSet.add(obs.date);
        });
    });
    const years = [...yearsSet];

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
    if (myChart instanceof Chart) {
        myChart.destroy();
    }
    const ctx = document.getElementById('countryChart').getContext('2d');
    myChart = new Chart(ctx, config);
}

getCountryGraph('Count_Person', ["United States", "China", "Russia", "Mexico", "Aruba", "India"]);