using System.Collections;
using System.Collections.Generic;
using UnityEngine;

public class GameSceneController : MonoBehaviour
{
    void Start()
    {
        bool playerX = GameManager.Instance.isPlayerX;
        string botFile = GameManager.Instance.botFile;

        Debug.Log("Gracz X? " + playerX);
        Debug.Log("Ładuję bota: " + botFile);

        // jeśli gracz O, bot wykonuje pierwszy ruch
        if(!playerX)
        {
            BotMove();
        }
    }

    void BotMove()
    {
        // wczytaj AI_Hard i wykonaj ruch
    }
}
