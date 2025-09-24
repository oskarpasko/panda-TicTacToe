using System.Collections;
using System.Collections.Generic;
using UnityEngine;
using UnityEngine.SceneManagement;
using UnityEngine.UI;

public class VsBotController : MonoBehaviour
{
    [Header("Board Buttons")]
    [SerializeField] private Button[] boardButtons; // 9 przycisków planszy

    [Header("Player symbol toggles")]
    [SerializeField] private Toggle toggleX;
    [SerializeField] private Toggle toggleO;

    [Header("Difficulty buttons")]
    [SerializeField] private Button buttonEasy;
    [SerializeField] private Button buttonMedium;
    [SerializeField] private Button buttonHard;

    [SerializeField] private Button buttonStart;

    private Color normalColor = Color.white;
    private Color selectedColor = Color.green;

    private bool gameStarted = false;

    void Start()
    {
        // Toggle X/O
        toggleX.onValueChanged.AddListener(delegate { SelectPlayerSymbol(); });
        toggleO.onValueChanged.AddListener(delegate { SelectPlayerSymbol(); });

        // Poziom trudności
        buttonEasy.onClick.AddListener(() => SelectDifficulty("Easy"));
        buttonMedium.onClick.AddListener(() => SelectDifficulty("Medium"));
        buttonHard.onClick.AddListener(() => SelectDifficulty("Hard"));

        // Start
        buttonStart.onClick.AddListener(StartGame);

        // domyślne wartości
        toggleX.isOn = true; // X domyślnie
        SelectDifficulty("Hard");

        // Początkowo wyłączamy przyciski planszy
        foreach (Button b in boardButtons)
            b.interactable = false;
    }

    private void SelectPlayerSymbol()
    {
        GameManager.Instance.isPlayerX = toggleX.isOn;
    }

    private void SelectDifficulty(string diff)
    {
        GameManager.Instance.botFile = "AI_" + diff;

        // Podświetlenie
        buttonEasy.image.color = diff == "Easy" ? selectedColor : normalColor;
        buttonMedium.image.color = diff == "Medium" ? selectedColor : normalColor;
        buttonHard.image.color = diff == "Hard" ? selectedColor : normalColor;
    }

    private void StartGame()
    {
        gameStarted = true;

        // włączamy przyciski planszy
        foreach (Button b in boardButtons)
            b.interactable = true;

        buttonStart.interactable = false;

        // Jeśli gracz O, bot wykonuje pierwszy ruch
        if (!GameManager.Instance.isPlayerX)
        {
            BotMove();
        }
    }

    private void BotMove()
    {
        Debug.Log("Bot wykonuje pierwszy ruch (AI Hard)...");
        // Tutaj wczytaj AI Hard i wykonaj ruch na planszy
        // np. boardButtons[randomIndex].GetComponentInChildren<Text>().text = "X";
    }
}
