# minesweeper-solver
Minesweeper auto player
A program to solve the minesweeper game automatically.

Each cell has two important features: 1. Content 2. The number of unknown neighbors.
This file after identifying the position of the game board on the screen and recognizing the cells (cell content using cell color) by putting these two features together (in the form of a two-digit number) for each cell (in a matrix), It checks whether the unknown cells next to it are mines or not, and after detecting the mines, Right-clicks or left-clicks on its neighbors with the mouse pointer.




steps:
1. Specifying the position of the game on the screen.
2. Clicking on the page (randomly) until an analyzable area opens.
3. Taking a screenshot of the game and recognizing the content of the cells by color.(if it is a new color, it will show you the image of the cell and ask you to tell it the content of the cell. It saves the color of numbers/min/flag/unknown cell/empty space in a text file and won't ask you agian)
4. Check the correlation of the cell with its neighbors to identify mines and fill the click list
5. Clicking





Note:

    - Download Minesweeper game.(http://www.minesweeper.info/downloads/games/MinesweeperX__1.15.zip)
    
    - Before running the file, make sure that the game screen is not under another window.
    
    - Do not delete the cell.jpg file!
    
    -If the game gives the message "Press Y to save or any key to continue..." it means that the continuation of the game is done based on the probability that I did not embed a method for this.  
    

Thank you.
    

