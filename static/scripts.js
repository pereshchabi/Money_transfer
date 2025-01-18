// scripts.js

document.addEventListener('DOMContentLoaded', () => {
    // Exemple : Ajouter une alerte pour confirmer l'envoi du formulaire
    const form = document.querySelector('form');
    if (form) {
        form.addEventListener('submit', (event) => {
            const confirmation = confirm('Êtes-vous sûr de vouloir soumettre ce formulaire ?');
            if (!confirmation) {
                event.preventDefault(); // Annule la soumission si l'utilisateur refuse
            }
        });
    }
});
