import cmd, os, sys
import main

class Shell(cmd.Cmd):
    prompt = '(mvn)'
    disk_path = ''
    infile_path = ''
    outfile_path = ''

    def do_job(self, arg):
        'inicia um novo job, reinicia todo o sistema'
        print("Hi, {}".format(arg))
        print("Sistema reiniciado")

    def do_disk(self, arg):
        'Simula disco do sistema nesta pasta do hospedeiro'
        self.disk_path = arg

    def do_directory(self, arg):
        'Lista o conteúdo da pasta do hospedeiro'
        dirs = os.listdir('.')
        for file in dirs:
            print(file)
        print('\n')

    def do_create(self, arg):
        'Cria no disco um novo arquivo, se ainda não existir'
        if not os.path.exists(arg):
            with open(arg, 'w'): pass
        print('file {} created'.format(arg))

    def do_delete(self, arg):
        'Remove do disco o arquivo indicado, se existir'
        if os.path.exists(arg):
            os.remove(arg)
        print('file {} deleted'.format(arg))

    def do_list(self, arg):
        'Apresenta o conteúdo do arquivo indicado, se existir'
        with open(arg, 'r') as file:
            print(file.read())

    def do_infile(self, arg):
        'Adota o arquivo indicado como a fita de entrada'
        self.infile_path = arg

    def do_outfile(self, arg):
        'Adota o arquivo indicado como a fita de saída'
        self.outfile_path = arg

    def do_diskfile(self, arg):
        'Adota o arquivo indicado como arquivo em disco'
        os.listdir(self.disk_path)

    def do_run(self, arg):
        'Executa o programa indicado (de sistema ou ususário)'
        if arg == "mvn":
            main.main()
        print("execucao terminada")

    def do_endjob(self, arg):
        'Finaliza pendências e termina o job corrente'
        sys.exit()

    def do_login(self, arg):
        'entrar legalmente do sistema'
        print("Welcome, {}".format(arg))

    def do_logout(self, arg):
        'sair legalmente do sistema'
        print("Bye, {}".format(arg))

    def do_prog(self, arg):
        'delimita as ações de um programa'
        pass

    def do_eprog(self, arg):
        'delimita as ações de um programa'
        pass

    def do_proc(self, arg):
        'especifica um tempo de processamento'
        pass

    def do_open(self, arg):
        'abrir arquivo sequencial'
        pass

    def do_close(self, arg):
        'fechar arquivo sequencial'
        pass

    def do_read(self, arg):
        'entrada sequencial em arquivo'
        pass

    def do_write(self, arg):
        'saída sequencial em arquivo'
        pass

    def do_in(self, arg):
        'entrada sequencial em dispositivo'
        print("Device {} in".format(arg))
    
    def do_out(self, arg):
        'saída sequencial em dispositivo'
        print("Device {} out".format(arg))

if __name__ == '__main__':
    mvn_shell().cmdloop()