console.clear();
('use strict');

window.onload = function() {
    document.getElementById('education_req_input').selectedIndex = 0;
};

// Global array to store files
let globalFiles = [];


// Drag and drop - single or multiple image files
// https://www.smashingmagazine.com/2018/01/drag-drop-file-uploader-vanilla-js/
// https://codepen.io/joezimjs/pen/yPWQbd?editors=1000
(function () {

    'use strict';
    
    // Four objects of interest: drop zones, input elements, gallery elements, and the files.
    // dataRefs = {files: [image files], input: element ref, gallery: element ref}

    const preventDefaults = event => {
        event.preventDefault();
        event.stopPropagation();
    };

    const highlight = event =>
        event.target.classList.add('highlight');
    
    const unhighlight = event =>
        event.target.classList.remove('highlight');

    const getInputAndGalleryRefs = element => {
        const zone = element.closest('.upload_dropZone') || false;
        const gallery = zone.querySelector('.upload_gallery') || false;
        const input = zone.querySelector('input[type="file"]') || false;
        return {input: input, gallery: gallery};
    }

    const handleDrop = event => {
        const dataRefs = getInputAndGalleryRefs(event.target);
        dataRefs.files = event.dataTransfer.files;
        handleFiles(dataRefs);
    }


    const eventHandlers = zone => {

        const dataRefs = getInputAndGalleryRefs(zone);
        if (!dataRefs.input) return;

        // Prevent default drag behaviors
        ;['dragenter', 'dragover', 'dragleave', 'drop'].forEach(event => {
        zone.addEventListener(event, preventDefaults, false);
        document.body.addEventListener(event, preventDefaults, false);
        });

        // Highlighting drop area when item is dragged over it
        ;['dragenter', 'dragover'].forEach(event => {
        zone.addEventListener(event, highlight, false);
        });
        ;['dragleave', 'drop'].forEach(event => {
        zone.addEventListener(event, unhighlight, false);
        });

        // Handle dropped files
        zone.addEventListener('drop', handleDrop, false);

        // Handle browse selected files
        dataRefs.input.addEventListener('change', event => {
        dataRefs.files = event.target.files;
        handleFiles(dataRefs);
        }, false);

    }


    // Initialise ALL dropzones
    const dropZones = document.querySelectorAll('.upload_dropZone');
    for (const zone of dropZones) {
        eventHandlers(zone);
    }


    // No 'image/gif' or PDF or webp allowed here, but it's up to your use case.
    // Double checks the input "accept" attribute
    const isImageFile = file => 
        ['application/pdf'].includes(file.type);


    function previewFiles(dataRefs) {
        if (!dataRefs.gallery) return;
        for (const file of dataRefs.files) {
        let reader = new FileReader();
        reader.readAsDataURL(file);
        reader.onloadend = function() {
            // let span = document.createElement('span');
            // span.className = 'upload_img mt-2';
            // span.setAttribute('te', file.name);
            // img.src = reader.result;
            let span = document.createElement('span');
            span.className = 'upload_img mt-2';
            span.setAttribute('te', file.name);
            span.textContent = file.name; 
            dataRefs.gallery.appendChild(span);
        }
        }
    }

    // Based on: https://flaviocopes.com/how-to-upload-files-fetch/
    
    // const imageUpload = dataRefs => {

    //     // Multiple source routes, so double check validity
    //     if (!dataRefs.files || !dataRefs.input) return;

    //     const url = dataRefs.input.getAttribute('data-post-url');
    //     if (!url) return;

    //     const name = dataRefs.input.getAttribute('data-post-name');
    //     if (!name) return;

    //     const formData = new FormData();
    //     formData.append(name, dataRefs.files);

    //     fetch(url, {
    //     method: 'POST',
    //     body: formData
    //     })
    //     .then(response => response.json())
    //     .then(data => {
    //     console.log('posted: ', data);
    //     if (data.success === true) {
    //         previewFiles(dataRefs);
    //     } else {
    //         console.log('URL: ', url, '  name: ', name)
    //     }
    //     })
    //     .catch(error => {
    //     console.error('errored: ', error);
    //     });
    // }


    // Handle both selected and dropped files
    const handleFiles = dataRefs => {

        let files = [...dataRefs.files];

        // Remove unaccepted file types
        files = files.filter(item => {
        if (!isImageFile(item)) {
            console.log('Not an image, ', item.type);
        }
        return isImageFile(item) ? item : null;
        });

        if (!files.length) return;
        dataRefs.files = files;

        // Add files to global array
        globalFiles = globalFiles.concat(files);

        previewFiles(dataRefs);
        // imageUpload(dataRefs);
    }

    document.getElementById('scout_query_submit').addEventListener('click', function() {
        // check if all fields are filled and files uploaded

        if (globalFiles.length === 0) {
            console.log('No files found');
            return;
        }

        const formData = new FormData();
        for (const file of globalFiles) {
            formData.append('files', file);
            // console.log('Data uploaded:', file.name);
        }

        // Get the value of the selected option in the education requirement select element
        const educationReqInput = document.getElementById('education_req_input');
        const educationReqValue = educationReqInput.value;
        formData.append('education_level', educationReqValue);

        // Get all the domain requirement data
        const domainContainer = document.getElementById('domains_tagsContainer');
        const domain_tags = domainContainer.getElementsByClassName('tag');
        let domain_tagsText = [];
        for (let domain_tg of domain_tags) {
            domain_tagsText.push(domain_tg.childNodes[0].nodeValue.trim());
        }
        formData.append('domains_list', JSON.stringify(domain_tagsText));

        // Get all the skill requirement data
        const skillstagsContainer = document.getElementById('skills_tagsContainer');
        const skills_tags = skillstagsContainer.getElementsByClassName('tag');
        let skills_tagsText = [];
        for (let skill_tg of skills_tags) {
            skills_tagsText.push(skill_tg.childNodes[0].nodeValue.trim());
        }
        formData.append('skills_list', JSON.stringify(skills_tagsText));

        // get the metrics weights
        const experiance_weight_val = document.getElementById('experiance_weight_input').value;
        formData.append('experiance_weight', experiance_weight_val);

        const relevance_weight_val = document.getElementById('relevance_weight_input').value;
        formData.append('relevance_weight', relevance_weight_val);

        const education_weight_val = document.getElementById('education_weight_input').value;
        formData.append('education_weight', education_weight_val);

        const skills_weight_val = document.getElementById('skills_weight_input').value;
        formData.append('skills_weight', skills_weight_val);

        fetch('/llm/upload/', {
            method: 'POST',
            body: formData,
            headers: {
                'X-CSRFToken': getCookie('csrftoken')
            }
        })
        .then(response => response.json())
        .then(data => {
            console.log('Success:', data);
            var session_id = data["data"]["session_id"]
            window.location.href = '/llm/scout/';
        })
        .catch(error => {
            console.error('Error:', error);
        });
    });

    
    function getCookie(name) {
        let cookieValue = null;
        if (document.cookie && document.cookie !== '') {
            const cookies = document.cookie.split(';');
            for (let i = 0; i < cookies.length; i++) {
                const cookie = cookies[i].trim();
                if (cookie.substring(0, name.length + 1) === (name + '=')) {
                    cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                    break;
                }
            }
        }
        return cookieValue;
    }

    })();

