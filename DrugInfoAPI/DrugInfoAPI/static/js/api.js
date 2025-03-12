async function searchDrug() {
    const drugName = document.getElementById('drugName').value.trim();
    const resultCard = document.getElementById('resultCard');

    if (!drugName) {
        alert('Please enter a drug name');
        return;
    }

    try {
        const response = await fetch(`/api/v1/drug?name=${encodeURIComponent(drugName)}`);
        const result = await response.json();

        if (result.status === 'success') {
            const data = result.data;

            // Update main drug information
            document.getElementById('drugTitle').textContent = data.name;
            document.getElementById('genericName').textContent = `Generic Name: ${data.generic_name}`;
            document.getElementById('drugClass').textContent = `Drug Class: ${data.drug_class}`;
            document.getElementById('description').textContent = data.description;

            // Clear and update lists
            const updateList = (elementId, items) => {
                const ul = document.getElementById(elementId);
                ul.innerHTML = '';
                items.forEach(item => {
                    const li = document.createElement('li');
                    li.className = 'list-group-item';
                    li.textContent = item;
                    ul.appendChild(li);
                });
            };

            updateList('commonUses', data.common_uses);
            updateList('typicalDosage', data.typical_dosage);
            updateList('sideEffects', data.side_effects);
            updateList('warnings', data.warnings);

            // Show the result card
            resultCard.classList.remove('d-none');
        } else {
            alert(result.message || 'Failed to retrieve drug information');
        }
    } catch (error) {
        alert('Error searching for drug information');
        console.error('Error:', error);
    }
}