document.addEventListener("DOMContentLoaded", function () {
    document.getElementById("subject").addEventListener("change", function () {
        let subjectId = this.value;
        let topicDropdown = document.getElementById("topic");

        topicDropdown.innerHTML = '<option value="">Select a Topic</option>';

        if (subjectId) {
            const url = (window.REVIZO_URLS?.getTopics || '/revizo/get-topics/') + `?subject_id=${subjectId}`;

            fetch(url, {
                headers: {
                    'Accept': 'application/json',
                    'X-Requested-With': 'XMLHttpRequest'
                },
                credentials: 'same-origin'
            })
            .then(response => {
                if (!response.ok) {
                    throw new Error(`HTTP error! status: ${response.status}`);
                }
                return response.json();
            })
            .then(data => {
                data.forEach(topic => {
                    let option = document.createElement("option");
                    option.value = topic.id;
                    option.textContent = topic.topic_name || topic.topic?.name || 'Unnamed Topic';
                    topicDropdown.appendChild(option);
                });
            })
            .catch(error => {
                console.error("Error fetching topics:", error);
                topicDropdown.innerHTML = '<option value="">Error loading topics</option>';
            });
        }
    });
});
