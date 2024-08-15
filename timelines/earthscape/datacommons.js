async function fetchCountyGeoIds(graphVariable, entityId) {
    // Fetch all geoIds containing geoId in name + are counties
    try {
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
        console.log("County Data:", data); // Log the data to inspect

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
            const node = data2.data[geoId].arcs;
            const stateName = node.containedInPlace.nodes[0]['name'];
            const countyName = node.name.nodes[0]['value'];
            countyData[geoId] = {
                name: countyName,
                state: stateName
            };
        });
        return countyData;
    } catch (error) {
        console.error('Error fetching county geo IDs:', error);
    }
}

async function fetchDataPoints(geoIds, graphVariable) {
    // Fetch data using geoIds list
    try {
        const url = `https://api.datacommons.org/v2/observation?key=AIzaSyCTI4Xz-UW_G2Q2RfknhcfdAnTHq5X5XuI&variable.dcids=${graphVariable}&${geoIds.map(id => `entity.dcids=${id}`).join('&')}`;
        const response = await fetch(url, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                "date": "",
                "select": ["date", "entity", "value", "variable"]
            })
        });
        const data = await response.json();
        return data;
    } catch (error) {
        console.error('Error fetching data points:', error);
    }
}

async function getFormattedData(graphVariable, entityId) {
    try {
        const geoIdsData = await fetchCountyGeoIds(graphVariable, entityId);
        const geoIds = Object.keys(geoIdsData);
        const forestCoverageData = await fetchDataPoints(geoIds, graphVariable);

        const formattedData = [];
        for (const geoId in geoIdsData) {
            formattedData.push({
                county: `${geoIdsData[geoId].name}, ${geoIdsData[geoId].state}`,
                observations: forestCoverageData.byVariable[graphVariable].byEntity[geoId].orderedFacets[0]['observations']
            });
        }
        return formattedData;
    } catch (error) {
        console.error('Error formatting data:', error);
    }
}

document.addEventListener('DOMContentLoaded', () => {
    const selectElement = document.getElementById('graphVariable');
    let graphVariable = 'Count_Person';
    let showAll = 'showTop5';
    let entityId = 'geoId/01';
    let myChart;    // Declare myChart in the broader scope

    // Function to update the H2 tag text and chart title
    const updateTexts = () => {
        const selectedOptionText = selectElement.options[selectElement.selectedIndex].text;
        if (myChart) {
            myChart.options.plugins.title.text = `${selectedOptionText}`;
            myChart.update();
        }
    };

    async function getGraph(showAll, graphVariable, entityId) {
        try {
            const data = await getFormattedData(graphVariable, entityId);

            // Get unique years
            let yearsSet = new Set();
            data.forEach(county => {
                county.observations.forEach(obs => {
                    yearsSet.add(obs.date);
                });
            });
            const years = [...yearsSet];

            // Showing all or top 5 or bottom 5 counties
            let selectedData;
            data.forEach(county => {
                county.averageLandCover = county.observations.reduce((sum, obs) => sum + obs.value, 0) / county.observations.length;
            });
            if (showAll == 'showTop5') {
                selectedData = data.sort((a, b) => b.averageLandCover - a.averageLandCover).slice(0, 5);
            } else if (showAll == 'showBottom5') {
                selectedData = data.sort((a, b) => a.averageLandCover - b.averageLandCover).slice(0, 5);
            } else {
                selectedData = data;
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
                            text: `${selectElement.options[selectElement.selectedIndex].text}`
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
        } catch (error) {
            console.error('Error getting graph:', error);
        }
    }

    updateTexts();
    getGraph(showAll, graphVariable, entityId);

    document.forms['countyShow'].addEventListener('change', function (event) {
        if (event.target.name === 'countyShow') {
            showAll = document.querySelector('input[name="countyShow"]:checked').value;
            getGraph(showAll, graphVariable, entityId);
        }
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

async function getCountryChart(chartVariable, facetId) {
    let myChart;    // Declare myChart in a broader scope
    
    // Get countries from URL
    try {
        let selectedCountries;
        const currentUrl = window.location.href;
        const equalParams = currentUrl.split('=');
        const countryParams = equalParams[equalParams.length - 1];
        selectedCountries = countryParams.split(',');

        console.log("Selected Countries:", selectedCountries);

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

        console.log("Country Codes Data:", data);

        // Make a dictionary of country code -> name
        const countryCodes = {};
        data.entities.forEach(entity => {
            if (entity.node && entity.candidates && entity.candidates[0] && entity.candidates[0].dcid) {
                countryCodes[entity.candidates[0].dcid] = entity.node;
            }
        });

        console.log("Country Codes:", countryCodes);

        // Fetch data for selected countries and selected variable
        const geoIds = Object.keys(countryCodes);
        const url = `https://api.datacommons.org/v2/observation?key=AIzaSyCTI4Xz-UW_G2Q2RfknhcfdAnTHq5X5XuI&variable.dcids=${chartVariable}&${geoIds.map(id => `entity.dcids=${id}`).join('&')}`;
        const response2 = await fetch(url, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                "date": "",
                "select": ["date", "entity", "value", "variable"]
            })
        });
        const data2 = await response2.json();

        console.log("Observation Data:", data2);

        // Get facetId based on a selected source
        for (const facetIdCheck in data2.facets) {
            if (data2.facets[facetIdCheck].provenanceUrl === "https://datacatalog.worldbank.org/dataset/world-development-indicators/") {
                facetId = facetIdCheck;
            }
        }

        console.log("Selected Facet ID:", facetId);

        // Use facetId to build formatted data
        const formattedData = [];
        for (const geoId of geoIds) {
            formattedData.push({
                country: countryCodes[geoId],
                observations: data2.byVariable[chartVariable].byEntity[geoId].orderedFacets.find((element) => element.facetId == facetId)['observations']
            });
        }

        console.log("Formatted Data:", formattedData);

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
        
        console.log("Datasets:", datasets);

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
    } catch (error) {
        console.error('Error getting country graph:', error);
    }
}

document.addEventListener('DOMContentLoaded', () => {
    getCountryChart('Count_Person', '3981252704');
});

window.addEventListener('hashChangeEvent', () => {
    getCountryChart('Count_Person', '3981252704');
});

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
    const url = `https://api.datacommons.org/v2/observation?key=AIzaSyCTI4Xz-UW_G2Q2RfknhcfdAnTHq5X5XuI&variable.dcids=${chartVariable}&${geoIds.map(id => `entity.dcids=${id}`).join('&')}`;
    const response2 = await fetch(url, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({
            "date": "",
            "select": ["date", "entity", "value", "variable"]
        })
    });
    const data2 = await response2.json();

    // Use facetId to build formatted data
    const formattedData = [];
    for (const geoId of geoIds) {
        formattedData.push({
            state: stateCodes[geoId],
            observations: data2.byVariable[chartVariable].byEntity[geoId].orderedFacets.find((element) => element.facetId == facetId)['observations']
        });
    }

    // Get unique years
    let yearsSet = new Set();
    formattedData.forEach(state => {
        state.observations.forEach(obs => {
            yearsSet.add(obs.date);
        });
    });
    const years = [...yearsSet].sort((a, b) => a - b);

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
    const chartVariable = 'Count_Person';
    const statesList = ['Florida', 'New Jersey', 'New York State', 'New Mexico', 'Alaska']; // 'New York' does not work, use 'New York State' - idk why
    const facetId = '2176550201';
    getStateChart(chartVariable, statesList, facetId);
});
