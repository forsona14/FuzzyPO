from Tkinter import *
import tkFont
from JRecInterface import JRecInterface
import codecs

def save(lang, interface):
    f = codecs.open("Text\SimpleUI_savedata.text", "w", "utf-8")
    f.write(str(lang) + "\n")
    f.write(interface.recommender_json_str() + "\n")
    f.close()

def iter(interface, textbox, res, lang=0):
    interface.response(res)
    req = interface.request()
    article = interface.request().article
    stats = interface.recommender.color_stats()
    textbox.delete('1.0', END)
    if lang==1:
        article_text = article.text
    else:
        article_text = article.text.replace(' ', '\n')
    textbox.insert(END, "Round: " + str(req.num) + "\n"
                   + "Doc ID: " + req.id + "\n"
                   + "Algo: " + req.info + "\n"
                   + "Colored Yes: " + str(stats[1]) + "  No: " + str(stats[0]) + "\n\n"
                   + article_text)
    save(lang, interface)

def ExampleUI(lang=0):
    tk = Tk()

    # Read Saved Data
    if lang == -1:
        try:
            f = codecs.open("Text\SimpleUI_savedata.text", "r", "utf-8")
        except:
            print "Read SimpleUI_savedata.text Error!"
            return
        lines = f.readlines()
        lang = int(lines[0][:-1])
        interface = JRecInterface(recommender_json_str=lines[1][:-1], lang=lang)
        f.close()
    else:
        interface = JRecInterface(lang=lang)

    if lang == 1:
        tk.title('SimpleUI       nachrichtenleicht     Sona Tithew')
    else:
        tk.title('SimpleUI       NHK_easy     Sona Tithew')
    tk.resizable(0, 0)
    textbox = Text(tk, font=tkFont.Font(size=12))
    req = interface.request()
    article = interface.request().article
    stats = interface.recommender.color_stats()
    if lang==1:
        article_text = article.text
    else:
        article_text = article.text.replace(' ', '\n')
    textbox.insert(END, "Round: " + str(req.num) + "\n"
                   + "Doc ID: " + req.id + "\n"
                   + "Algo: " + req.info + "\n"
                   + "Colored Yes: " + str(stats[1]) + "  No: " + str(stats[0]) + "\n\n"
                   + article_text)
    save(lang, interface)
    textbox.grid(row=0, column=0, columnspan=5)
    m = IntVar()
    m.set(2)
    #Radiobutton(tk, text='0%', variable=m, value=4).grid(row=1, column=0, sticky=N + S + E + W)
    #Radiobutton(tk, text='25%', variable=m, value=3).grid(row=1, column=1, sticky=N + S + E + W)
    #Radiobutton(tk, text='50%', variable=m, value=2).grid(row=1, column=2, sticky=N + S + E + W)
    #Radiobutton(tk, text='75%', variable=m, value=1).grid(row=1, column=3, sticky=N + S + E + W)
    #Radiobutton(tk, text='100%', variable=m, value=0).grid(row=1, column=4, sticky=N + S + E + W)
    #e = IntVar()
    #e.set(1)
    # Radiobutton(tk, text='I prefer easier articles.', variable=e, value=0).grid(row=2, column=1, sticky=N + S + E + W)
    # Radiobutton(tk, text='I enjoy this article!', variable=e, value=1).grid(row=2, column=2, sticky=N + S + E + W)
    # Radiobutton(tk, text='I prefer harder articles.', variable=e, value=2).grid(row=2, column=3, sticky=N + S + E + W)
    # Button(tk, text='Submit', height=1, width=12, font=tkFont.Font(size=24), command = lambda: self.kb_iter(textbox, m.get(), e.get())).grid(row=3, column=1, columnspan=3)
    Button(tk, text='Yes', height=1, width=22, font=tkFont.Font(size=10),
           command=lambda: iter(interface, textbox, True, lang)).grid(row=1, column=1, sticky=N + S + E + W)
    Button(tk, text='No', height=1, width=22, font=tkFont.Font(size=10),
           command=lambda: iter(interface, textbox, False, lang)).grid(row=1, column=2, sticky=N + S + E + W)
    tk.mainloop()

if __name__ == "__main__":
    ExampleUI(lang=1)