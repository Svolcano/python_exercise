import wx


class HelloFrame(wx.Frame):

    def __init__(self, *args, **kw):
        super(HelloFrame, self).__init__(*args, **kw)
        pn1 = wx.Panel(self)
        st = wx.StaticText(pn1, label="hello world!", pos=(25, 25))
        font = st.GetFont()
        font.PointSize += 10
        font = font.Bold()
        st.SetFont(font)

        self.makeMenuBar()

        self.CreateStatusBar()
        self.SetStatusText("Welcome to wxPython!")

    def makeMenuBar(self):
        fileMenu = wx.Menu()
        helloItem = fileMenu.Append(-1, "&Hello...\tCtrl-H", "help string shown in status bar for this menu")
        fileMenu.AppendSeparator()

        exitItem = fileMenu.Append(wx.ID_EXIT)

        helpMenu = wx.Menu()
        aboutItem = helpMenu.Append(wx.ID_ABOUT)

        menuBar = wx.MenuBar()
        menuBar.Append(fileMenu, '&File')
        menuBar.Append(helpMenu, "&Help")

        self.SetMenuBar(menuBar)

        self.Bind(wx.EVT_MENU, self.OnHello, helloItem)
        self.Bind(wx.EVT_MENU, self.OnExit, exitItem)
        self.Bind(wx.EVT_MENU, self.OnAbout, aboutItem)

    def OnExit(self, event):
        self.Close()

    def OnHello(self, event):
        wx.MessageBox("Hello again from wxPython")

    def OnAbout(self, event):
        wx.MessageBox("This is a wxPython hello World sample",
                      "About Hello World 2",
                      wx.OK | wx.ICON_INFORMATION
                      )


if __name__ == '__main__':
    app = wx.App()
    frm = HelloFrame(None, title='Hello world2')
    frm.Show()
    app.MainLoop()
