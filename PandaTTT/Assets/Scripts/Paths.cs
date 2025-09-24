using System.Collections;
using System.Collections.Generic;
using UnityEngine;
using UnityEngine.SceneManagement;

public class Paths : MonoBehaviour
{
    public void vsBot()
    {
        SceneManager.LoadScene("vsBot");
    }

    public void MainMenu()
    {
        SceneManager.LoadScene("MainMenu");
    }
}
