document.getElementById('domains_list_input').addEventListener('keypress', function(event) {
    if (event.key === 'Enter') {
        event.preventDefault();
        const inputValue = this.value.trim();
        if (inputValue) {
            addTag(inputValue, 'domains_tagsContainer');
            this.value = '';
        }
    }
});

document.getElementById('skills_list_input').addEventListener('keypress', function(event) {
    if (event.key === 'Enter') {
        event.preventDefault();
        const inputValue = this.value.trim();
        if (inputValue) {
            addTag(inputValue, 'skills_tagsContainer');
            this.value = '';
        }
    }
});

function addTag(value, container_name) {
    const tag = document.createElement('span');
    tag.className = 'tag';
    tag.textContent = value;

    const removeTag = document.createElement('span');
    removeTag.className = 'remove-tag';
    removeTag.textContent = 'x';
    removeTag.onclick = function() {
        this.parentElement.remove();
    };

    tag.appendChild(removeTag);
    document.getElementById(container_name).appendChild(tag);
}